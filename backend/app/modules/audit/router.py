from fastapi import APIRouter, Query, HTTPException, Request
from datetime import datetime
from typing import Optional
from app.services.audit_logger import AuditLogger
from app.utils.logger import get_logger, LogCategory

router = APIRouter()


@router.get("/api/v1/audit/logs")
async def get_audit_logs(
    user_id: Optional[int] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    skip: int = Query(0, ge=0)
):
    """
    Retrieve audit logs with optional filtering
    
    Query Parameters:
    - user_id: Filter by user ID
    - resource_type: Filter by resource type (resume, interview, gamification, etc.)
    - start_date: Filter logs after this date (ISO format)
    - end_date: Filter logs before this date (ISO format)
    - limit: Number of records to return (default: 100, max: 1000)
    - skip: Number of records to skip for pagination
    
    Returns:
    - total: Total number of matching records
    - logs: Array of audit log entries
    """
    try:
        start = None
        end = None
        
        if start_date:
            start = datetime.fromisoformat(start_date)
        
        if end_date:
            end = datetime.fromisoformat(end_date)
        
        result = AuditLogger.get_audit_logs(
            user_id=user_id,
            resource_type=resource_type,
            start_date=start,
            end_date=end,
            limit=limit,
            skip=skip
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        get_logger().log_error(LogCategory.SYSTEM, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/audit/logs/export")
async def export_audit_logs(
    user_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    format: str = Query("json", pattern="^(json|csv)$")
):
    """
    Export audit logs for compliance and analysis
    
    Query Parameters:
    - user_id: Filter by user ID
    - start_date: Filter logs after this date (ISO format)
    - end_date: Filter logs before this date (ISO format)
    - format: Export format (json or csv)
    
    Returns:
    - format: The format used for export
    - total_records: Number of exported records
    - data: Exported audit logs
    """
    try:
        start = None
        end = None
        
        if start_date:
            start = datetime.fromisoformat(start_date)
        
        if end_date:
            end = datetime.fromisoformat(end_date)
        
        result = AuditLogger.export_audit_logs(
            user_id=user_id,
            start_date=start,
            end_date=end,
            format=format
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        get_logger().log_action(
            LogCategory.SYSTEM,
            "audit_logs_exported",
            details={"format": format, "records": result.get("total_records", 0)}
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        get_logger().log_error(LogCategory.SYSTEM, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/v1/audit/logs/clear")
async def clear_old_audit_logs(
    days: int = Query(90, ge=7, le=365)
):
    """
    Clear audit logs older than specified days
    
    Query Parameters:
    - days: Number of days to retain (must be between 7 and 365, default: 90)
    
    Returns:
    - success: Whether operation was successful
    - deleted_records: Number of records deleted
    - cutoff_date: Date before which logs were deleted
    """
    try:
        result = AuditLogger.clear_old_audit_logs(days=days)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        get_logger().log_action(
            LogCategory.SYSTEM,
            "audit_logs_cleared",
            details={"deleted_records": result.get("deleted_records", 0), "retention_days": days}
        )
        
        return result
    except Exception as e:
        get_logger().log_error(LogCategory.SYSTEM, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/audit/stats")
async def get_audit_statistics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None)
):
    """
    Get audit log statistics and analytics
    
    Query Parameters:
    - start_date: Start date for analysis (ISO format)
    - end_date: End date for analysis (ISO format)
    
    Returns:
    - total_actions: Total number of actions
    - total_users: Unique users who performed actions
    - resource_breakdown: Actions grouped by resource type
    - action_breakdown: Actions grouped by action type
    - http_status_breakdown: Actions grouped by HTTP status
    - top_endpoints: Most accessed endpoints
    """
    try:
        from sqlalchemy import func
        from app.database.models import AuditLog
        from app.database.session import SessionLocal
        
        db = SessionLocal()
        
        try:
            query = db.query(AuditLog)
            
            start = None
            end = None
            
            if start_date:
                start = datetime.fromisoformat(start_date)
                query = query.filter(AuditLog.created_at >= start)
            
            if end_date:
                end = datetime.fromisoformat(end_date)
                query = query.filter(AuditLog.created_at <= end)
            
            # Total stats
            total_actions = query.count()
            total_users = db.query(AuditLog.user_id).distinct().count()
            
            # Breakdowns
            resource_breakdown = {}
            for resource_type, count in db.query(
                AuditLog.resource_type,
                func.count(AuditLog.id)
            ).group_by(AuditLog.resource_type).all():
                resource_breakdown[resource_type or "unknown"] = count
            
            action_breakdown = {}
            for action, count in db.query(
                AuditLog.action,
                func.count(AuditLog.id)
            ).group_by(AuditLog.action).all():
                action_breakdown[action or "unknown"] = count
            
            status_breakdown = {}
            for status, count in db.query(
                AuditLog.status_code,
                func.count(AuditLog.id)
            ).group_by(AuditLog.status_code).all():
                status_breakdown[str(status or "unknown")] = count
            
            # Top endpoints
            top_endpoints = {}
            for endpoint, count in db.query(
                AuditLog.endpoint,
                func.count(AuditLog.id)
            ).group_by(AuditLog.endpoint).order_by(
                func.count(AuditLog.id).desc()
            ).limit(10).all():
                top_endpoints[endpoint or "unknown"] = count
            
            return {
                "total_actions": total_actions,
                "total_users": total_users,
                "date_range": {
                    "start": start.isoformat() if start else None,
                    "end": end.isoformat() if end else None
                },
                "resource_breakdown": resource_breakdown,
                "action_breakdown": action_breakdown,
                "http_status_breakdown": status_breakdown,
                "top_endpoints": top_endpoints
            }
        finally:
            db.close()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        get_logger().log_error(LogCategory.SYSTEM, e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/v1/audit/user/{user_id}/timeline")
async def get_user_activity_timeline(user_id: int):
    """
    Get a timeline of all activities for a specific user
    
    Path Parameters:
    - user_id: The user ID to track
    
    Returns:
    - user_id: The requested user ID
    - total_actions: Total number of actions by this user
    - timeline: Chronological list of all user actions
    """
    try:
        result = AuditLogger.get_audit_logs(
            user_id=user_id,
            limit=10000,  # Get all records
            skip=0
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "user_id": user_id,
            "total_actions": result.get("total", 0),
            "timeline": result.get("logs", [])
        }
    except Exception as e:
        get_logger().log_error(LogCategory.SYSTEM, e)
        raise HTTPException(status_code=500, detail=str(e))
