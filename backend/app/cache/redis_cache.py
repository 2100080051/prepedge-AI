"""
Redis caching layer for hot data.
Implements cache-aside pattern with TTL.
"""

from redis import Redis
from functools import wraps
import json
import logging
from typing import Any, Callable, Optional
from datetime import timedelta

logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for application data."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize Redis connection."""
        self.redis = Redis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 3600  # 1 hour
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache with TTL."""
        try:
            ttl = ttl or self.default_ttl
            self.redis.setex(
                key,
                timedelta(seconds=ttl),
                json.dumps(value, default=str)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache."""
        try:
            self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
    
    def get_or_set(self, key: str, callback: Callable, ttl: int = None) -> Any:
        """Get from cache or call callback to set."""
        # Try to get from cache
        value = self.get(key)
        if value is not None:
            logger.info(f"Cache HIT: {key}")
            return value
        
        # Cache miss - get fresh data
        logger.info(f"Cache MISS: {key}")
        value = callback()
        self.set(key, value, ttl)
        return value


# Singleton instance
_cache_instance: Optional[RedisCache] = None

def get_cache() -> RedisCache:
    """Get or create Redis cache instance."""
    global _cache_instance
    if _cache_instance is None:
        from app.config import settings
        _cache_instance = RedisCache(settings.redis_url)
    return _cache_instance


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments."""
    key_parts = [*args]
    key_parts.extend(f"{k}:{v}" for k, v in kwargs.items())
    return ":".join(str(part) for part in key_parts)


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Build cache key
            cache_k = f"{key_prefix or func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try cache first
            result = cache.get(cache_k)
            if result is not None:
                return result
            
            # Compute and cache
            result = func(*args, **kwargs)
            cache.set(cache_k, result, ttl)
            return result
        
        return wrapper
    return decorator


# Cache key patterns
CACHE_KEYS = {
    "trending_companies": "companies:trending:*",
    "company_details": "company:details:*",
    "company_jobs": "company:jobs:*",
    "recommendations": "recommendations:*",
    "user_stats": "user:stats:*",
    "all": "*"
}


async def invalidate_company_cache(company_id: int):
    """Invalidate cached data for a company."""
    cache = get_cache()
    cache.delete(f"company:details:{company_id}")
    cache.delete(f"company:jobs:{company_id}")
    logger.info(f"Invalidated cache for company {company_id}")


async def invalidate_user_cache(user_id: int):
    """Invalidate cached data for a user."""
    cache = get_cache()
    cache.delete(f"user:stats:{user_id}")
    cache.delete(f"recommendations:{user_id}")
    logger.info(f"Invalidated cache for user {user_id}")
