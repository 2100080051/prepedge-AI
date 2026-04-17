import time
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Request
import json
from functools import wraps

from app.utils.logger import get_logger, LogCategory
from app.database.models import AuditLog
from app.database.session import SessionLocal


class AuditLogger:
    """
    Comprehensive audit trail logger
    Tracks all user actions and system events in database
    """

    @staticmethod
    def log_audit(
        user_id: Optional[int] = None,
        action: str = "user_action",
        resource_type: str = "general",
        resource_id: Optional[int] = None,
        method: str = "GET",
        endpoint: str = "/",
        status_code: int = 200,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_body: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        duration_ms: float = 0
    ) -> Dict[str, Any]:
        """
        Create an audit log entry in database
        """
        try:
            db = SessionLocal()
            
            audit_entry = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                ip_address=ip_address,
                user_agent=user_agent,
                request_body=json.dumps(request_body) if request_body else None,
                response_data=json.dumps(response_data) if response_data else None,
                error_message=error_message,
                duration_ms=duration_ms,
                created_at=datetime.utcnow()
            )
            
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
            
            return {
                "id": audit_entry.id,
                "timestamp": audit_entry.created_at.isoformat(),
                "user_id": user_id,
                "action": action,
                "status_code": status_code
            }
        except Exception as e:
            get_logger().log_error(
                LogCategory.SYSTEM,
                e,
                user_id=user_id,
                context={"action": action}
            )
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    @staticmethod
    def get_audit_logs(
        user_id: Optional[int] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Retrieve audit logs with optional filters
        """
        try:
            db = SessionLocal()
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if resource_type:
                query = query.filter(AuditLog.resource_type == resource_type)
            
            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)
            
            # Get total count
            total = query.count()
            
            # Apply pagination and ordering
            logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
            
            return {
                "total": total,
                "skip": skip,
                "limit": limit,
                "logs": [
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "resource_id": log.resource_id,
                        "method": log.method,
                        "endpoint": log.endpoint,
                        "status_code": log.status_code,
                        "ip_address": log.ip_address,
                        "duration_ms": log.duration_ms,
                        "created_at": log.created_at.isoformat(),
                        "error_message": log.error_message
                    }
                    for log in logs
                ]
            }
        except Exception as e:
            get_logger().log_error(LogCategory.SYSTEM, e)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    @staticmethod
    def export_audit_logs(
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export audit logs for compliance and analysis
        """
        try:
            db = SessionLocal()
            query = db.query(AuditLog)
            
            if user_id:
                query = query.filter(AuditLog.user_id == user_id)
            
            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)
            
            logs = query.order_by(AuditLog.created_at.asc()).all()
            
            if format == "json":
                export_data = [
                    {
                        "id": log.id,
                        "user_id": log.user_id,
                        "action": log.action,
                        "resource_type": log.resource_type,
                        "method": log.method,
                        "endpoint": log.endpoint,
                        "status_code": log.status_code,
                        "ip_address": log.ip_address,
                        "user_agent": log.user_agent,
                        "duration_ms": log.duration_ms,
                        "created_at": log.created_at.isoformat(),
                        "error_message": log.error_message
                    }
                    for log in logs
                ]
            elif format == "csv":
                # CSV export
                export_data = logs
            else:
                return {"error": "Unsupported format"}
            
            return {
                "format": format,
                "total_records": len(logs),
                "data": export_data
            }
        except Exception as e:
            get_logger().log_error(LogCategory.SYSTEM, e)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()

    @staticmethod
    def clear_old_audit_logs(days: int = 90) -> Dict[str, Any]:
        """
        Clear audit logs older than specified days
        """
        try:
            db = SessionLocal()
            cutoff_date = datetime.utcnow() - __import__('datetime').timedelta(days=days)
            
            # Delete old logs
            deleted = db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).delete()
            
            db.commit()
            
            return {
                "success": True,
                "deleted_records": deleted,
                "cutoff_date": cutoff_date.isoformat()
            }
        except Exception as e:
            get_logger().log_error(LogCategory.SYSTEM, e)
            return {"error": str(e)}
        finally:
            if 'db' in locals():
                db.close()


def audit_endpoint(
    resource_type: str = "general",
    action_description: str = "user_action"
):
    """
    Decorator for auditing API endpoints
    Automatically logs all requests and responses
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(request: Request, *args, **kwargs):
            start_time = time.time()
            user_id = getattr(request.state, 'user_id', None)
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent', '')
            
            try:
                result = await func(request, *args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Log successful request
                AuditLogger.log_audit(
                    user_id=user_id,
                    action=action_description,
                    resource_type=resource_type,
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=200,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    duration_ms=duration_ms
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Log error request
                AuditLogger.log_audit(
                    user_id=user_id,
                    action=action_description,
                    resource_type=resource_type,
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=500,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                raise
        
        @wraps(func)
        def sync_wrapper(request: Request, *args, **kwargs):
            start_time = time.time()
            user_id = getattr(request.state, 'user_id', None)
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get('user-agent', '')
            
            try:
                result = func(request, *args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                AuditLogger.log_audit(
                    user_id=user_id,
                    action=action_description,
                    resource_type=resource_type,
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=200,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    duration_ms=duration_ms
                )
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                AuditLogger.log_audit(
                    user_id=user_id,
                    action=action_description,
                    resource_type=resource_type,
                    method=request.method,
                    endpoint=str(request.url.path),
                    status_code=500,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                raise
        
        # Check if function is async
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
