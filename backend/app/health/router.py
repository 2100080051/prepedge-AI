"""
Health Check Endpoints
Comprehensive system health monitoring
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from datetime import datetime
import os

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check():
    """Basic health check - server is running"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "PrepEdge AI Backend",
    }


@router.get("/live")
def liveness_check():
    """Kubernetes liveness probe - server is alive"""
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe - server is ready to handle requests"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "disconnected",
            "error": str(e),
        }, 503


@router.get("/detailed")
def detailed_health_check(db: Session = Depends(get_db)):
    """Comprehensive health check with all system details"""
    
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # 1. Server check
    health_status["checks"]["server"] = {
        "status": "up",
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # 2. Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "connected",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
        health_status["status"] = "degraded"
    
    # 3. Environment check
    environment = os.getenv("ENVIRONMENT", "unknown")
    health_status["checks"]["environment"] = {
        "status": "configured",
        "environment": environment,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # 4. Database pool check (if available)
    try:
        pool = db.get_bind().pool
        health_status["checks"]["database_pool"] = {
            "status": "active",
            "size": pool.size() if hasattr(pool, 'size') else "N/A",
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else "N/A",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        health_status["checks"]["database_pool"] = {
            "status": "unknown",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    # Determine overall status
    if health_status["checks"].get("database", {}).get("status") == "disconnected":
        return health_status, 503
    
    return health_status
