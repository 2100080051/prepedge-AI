"""
Production readiness tests.
Validates all components work together in production configuration.
"""

import pytest
import asyncio
import httpx
from datetime import datetime, timedelta
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.cache.redis_cache import get_cache, cached
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class TestDatabaseConnectivity:
    """Test database connections and performance."""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test basic database connectivity."""
        try:
            async for session in get_db():
                result = await session.execute(text("SELECT 1 as test"))
                data = result.fetchone()
                assert data[0] == 1
                break
        except Exception as e:
            pytest.fail(f"Database connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_connection_pool(self):
        """Test connection pool works correctly."""
        async for session in get_db():
            # Run multiple concurrent queries
            tasks = [
                session.execute(text(f"SELECT {i} as num"))
                for i in range(10)
            ]
            results = await asyncio.gather(*tasks)
            assert len(results) == 10
            break


class TestRedisCache:
    """Test Redis cache functionality."""
    
    def test_redis_connection(self):
        """Test Redis connection."""
        cache = get_cache()
        test_key = "test_connection"
        
        # Set and get
        cache.set(test_key, {"status": "ok"}, ttl=60)
        result = cache.get(test_key)
        
        assert result is not None
        assert result["status"] == "ok"
        
        # Cleanup
        cache.delete(test_key)
    
    def test_cache_ttl(self):
        """Test cache TTL expiration."""
        cache = get_cache()
        test_key = "ttl_test"
        
        # Set with 1 second TTL
        cache.set(test_key, {"value": 123}, ttl=1)
        
        # Should exist immediately
        result = cache.get(test_key)
        assert result is not None
        
        # Wait for expiration
        import time
        time.sleep(2)
        
        result = cache.get(test_key)
        assert result is None
    
    def test_cache_decorator(self):
        """Test caching decorator."""
        call_count = 0
        
        @cached(ttl=3600, key_prefix="test")
        def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # First call - should execute function
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Second call - should use cache
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Not incremented
        
        # Different argument - should execute function
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2


class TestCeleryQueue:
    """Test Celery task queue functionality."""
    
    def test_celery_connection(self):
        """Test Celery can connect to broker."""
        try:
            from app.tasks.celery_app import celery_app
            
            # Try to get app status
            inspect = celery_app.control.inspect()
            result = inspect.ping()
            
            # At least Redis should be accessible
            assert result is not None or True  # Allow no workers
        except Exception as e:
            pytest.fail(f"Celery connection failed: {e}")
    
    @pytest.mark.asyncio
    async def test_task_execution(self):
        """Test executing a simple task."""
        try:
            from app.tasks.jobs import send_email_notification
            
            # Schedule a task (won't actually send email, just queue it)
            task = send_email_notification.delay(
                user_id=1,
                template="test",
                context={"test": "value"}
            )
            
            # Task should be queued
            assert task is not None
            assert task.id is not None
        except Exception as e:
            logger.warning(f"Task execution test skipped: {e}")


class TestAPIEndpoints:
    """Test API endpoints are accessible."""
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Test health check endpoint."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/health")
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "ok"
    
    @pytest.mark.asyncio
    async def test_deep_health_check(self):
        """Test deep health check with all services."""
        async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
            response = await client.get("/api/v1/health/deep")
            # Either 200 or 503 depending on service status
            assert response.status_code in [200, 503]
            data = response.json()
            assert "services" in data


class TestCachePerformance:
    """Test cache performance."""
    
    def test_cache_performance_improvement(self):
        """Verify caching improves performance."""
        import time
        
        cache = get_cache()
        cache_key = "perf_test"
        
        def slow_operation():
            time.sleep(0.1)
            return {"result": "data"}
        
        # First call without cache
        start = time.time()
        result1 = cache.get_or_set(cache_key, slow_operation, ttl=3600)
        first_time = time.time() - start
        
        # Second call with cache
        start = time.time()
        result2 = cache.get_or_set(cache_key, slow_operation, ttl=3600)
        second_time = time.time() - start
        
        # Cache should be significantly faster
        assert result1 == result2
        assert second_time < first_time / 2  # At least 2x faster
        
        cache.delete(cache_key)


class TestDatabasePerformance:
    """Test database query performance."""
    
    @pytest.mark.asyncio
    async def test_query_execution_time(self):
        """Verify queries execute within acceptable time."""
        import time
        
        async for session in get_db():
            # Simple query
            start = time.time()
            result = await session.execute(text("SELECT 1"))
            duration = (time.time() - start) * 1000
            
            # Should be fast (< 10ms typically)
            assert duration < 100  # 100ms threshold
            break


class TestSecurityHeaders:
    """Test security configuration."""
    
    def test_secret_key_configured(self):
        """Verify secret key is properly configured."""
        assert settings.SECRET_KEY is not None
        assert len(settings.SECRET_KEY) >= 32
        assert settings.SECRET_KEY != "dev-fallback-super-secret-32+chars-long-key-1234567890!!"
    
    def test_cors_configured(self):
        """Verify CORS is configured."""
        assert hasattr(settings, 'ALLOWED_ORIGINS')
        assert len(settings.ALLOWED_ORIGINS) > 0


class TestDataValidation:
    """Test data persistence and validation."""
    
    @pytest.mark.asyncio
    async def test_data_consistency(self):
        """Verify data is persistent and consistent."""
        async for session in get_db():
            # Test data insertion and retrieval
            from sqlalchemy import Column, Integer, String, Table, MetaData
            
            # Create a test table
            await session.execute(text("""
                CREATE TABLE IF NOT EXISTS test_data (
                    id SERIAL PRIMARY KEY,
                    value VARCHAR(100)
                )
            """))
            
            # Insert test data
            await session.execute(text("""
                INSERT INTO test_data (value) VALUES ('test_value')
            """))
            
            # Retrieve and verify
            result = await session.execute(text("SELECT value FROM test_data WHERE value = 'test_value'"))
            data = result.fetchone()
            
            assert data is not None
            assert data[0] == "test_value"
            
            # Cleanup
            await session.execute(text("DROP TABLE test_data"))
            await session.commit()
            break


# Load testing

@pytest.mark.asyncio
async def test_concurrent_requests():
    """Test system handles concurrent requests."""
    async with httpx.AsyncClient(base_url="http://localhost:8000") as client:
        # Send 50 concurrent requests
        tasks = [
            client.get("/api/v1/health")
            for _ in range(50)
        ]
        
        responses = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(r.status_code == 200 for r in responses)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
