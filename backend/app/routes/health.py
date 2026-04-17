"""
Health check endpoints for monitoring application status.
Used by load balancers and monitoring systems.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_db
from app.cache.redis_cache import get_cache
from app.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT,
        "app_name": settings.APP_NAME,
    }


@router.get("/deep")
async def deep_health_check(session: AsyncSession = Depends(get_db)):
    """
    Comprehensive health check with all service dependencies.
    Returns detailed status of all critical services.
    """
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": "unknown",
        "services": {},
    }
    
    # Check API
    results["services"]["api"] = {"status": "ok", "version": settings.APP_NAME}
    
    # Check Database
    try:
        await session.execute(text("SELECT 1"))
        results["services"]["database"] = {"status": "ok", "type": "postgresql"}
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        results["services"]["database"] = {"status": "error", "message": str(e)}
    
    # Check Redis Cache
    try:
        cache = get_cache()
        test_key = "health_check_test"
        cache.set(test_key, {"test": "value"}, ttl=10)
        cached_val = cache.get(test_key)
        if cached_val:
            results["services"]["redis"] = {"status": "ok", "type": "redis"}
        else:
            raise Exception("Cache set/get failed")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        results["services"]["redis"] = {"status": "error", "message": str(e)}
    
    # Check Celery
    try:
        from app.tasks.celery_app import celery_app
        
        # Try to ping celery
        celery_status = celery_app.control.inspect().ping()
        if celery_status:
            results["services"]["celery"] = {
                "status": "ok",
                "workers": len(celery_status)
            }
        else:
            results["services"]["celery"] = {
                "status": "degraded",
                "message": "No workers available"
            }
    except Exception as e:
        logger.error(f"Celery health check failed: {e}")
        results["services"]["celery"] = {"status": "error", "message": str(e)}
    
    # Determine overall status
    service_statuses = [s.get("status") for s in results["services"].values()]
    if all(s == "ok" for s in service_statuses):
        results["status"] = "healthy"
    elif all(s != "error" for s in service_statuses):
        results["status"] = "degraded"
    else:
        results["status"] = "unhealthy"
    
    # Return 503 if unhealthy
    if results["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=results)
    
    return results


@router.get("/ready")
async def readiness_check(session: AsyncSession = Depends(get_db)):
    """
    Kubernetes-style readiness check.
    Returns 200 if service is ready to accept traffic.
    """
    try:
        # Check critical dependencies for readiness
        await session.execute(text("SELECT 1"))
        cache = get_cache()
        cache.redis.ping()
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail={"status": "not_ready", "message": str(e)}
        )


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness check.
    Returns 200 if service is alive and should not be restarted.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
