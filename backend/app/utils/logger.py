import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import traceback
from contextlib import contextmanager
import threading

# Thread-local storage for request context
_request_context = threading.local()


class LogLevel(Enum):
    """Custom log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogCategory(Enum):
    """Log categories for structured logging"""
    AUTH = "AUTH"
    RESUME = "RESUME"
    INTERVIEW = "INTERVIEW"
    GAMIFICATION = "GAMIFICATION"
    LLM = "LLM"
    DATABASE = "DATABASE"
    EXTERNAL_API = "EXTERNAL_API"
    USER_ACTION = "USER_ACTION"
    SYSTEM = "SYSTEM"
    PERFORMANCE = "PERFORMANCE"
    ERROR = "ERROR"


class StructuredLogger:
    """
    Structured logging system for detailed audit trails
    Logs all operations with context for debugging and monitoring
    """

    def __init__(self, name: str = "PrepEdgeAI"):
        self.logger = logging.getLogger(name)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging handlers"""
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # File handler for detailed logs
        file_handler = logging.FileHandler("app.log")
        file_handler.setLevel(logging.DEBUG)

        # Error file handler
        error_handler = logging.FileHandler("app_errors.log")
        error_handler.setLevel(logging.ERROR)

        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        error_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.DEBUG)

    def log_action(
        self,
        category: LogCategory,
        action: str,
        user_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
        status: str = "success"
    ):
        """
        Log a user action or system event
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category.value,
            "action": action,
            "user_id": user_id,
            "status": status,
            "details": details or {},
            "request_id": self._get_request_id()
        }

        self.logger.info(json.dumps(log_entry))
        return log_entry

    def log_error(
        self,
        category: LogCategory,
        error: Exception,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        Log an error with full traceback
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": category.value,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "user_id": user_id,
            "context": context or {},
            "request_id": self._get_request_id()
        }

        self.logger.error(json.dumps(log_entry))
        return log_entry

    def log_api_call(
        self,
        service: str,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None
    ):
        """
        Log API call for monitoring
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": "API",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "user_id": user_id,
            "request_id": request_id or self._get_request_id()
        }

        if status_code >= 400:
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))

        return log_entry

    def log_database_operation(
        self,
        operation: str,
        table: str,
        duration_ms: float,
        rows_affected: int = 0,
        success: bool = True
    ):
        """
        Log database operations
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": "DATABASE",
            "operation": operation,
            "table": table,
            "duration_ms": duration_ms,
            "rows_affected": rows_affected,
            "success": success,
            "request_id": self._get_request_id()
        }

        self.logger.info(json.dumps(log_entry))
        return log_entry

    def log_llm_call(
        self,
        provider: str,
        model: str,
        tokens_used: int,
        duration_ms: float,
        success: bool = True,
        error: Optional[str] = None
    ):
        """
        Log LLM API calls for cost tracking and monitoring
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": "LLM",
            "provider": provider,
            "model": model,
            "tokens_used": tokens_used,
            "duration_ms": duration_ms,
            "success": success,
            "error": error,
            "request_id": self._get_request_id()
        }

        if not success:
            self.logger.error(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))

        return log_entry

    def log_performance_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "ms",
        component: str = "system"
    ):
        """
        Log performance metrics
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "category": "PERFORMANCE",
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "component": component,
            "request_id": self._get_request_id()
        }

        self.logger.info(json.dumps(log_entry))
        return log_entry

    def set_request_context(self, request_id: str, user_id: Optional[int] = None, metadata: Optional[Dict] = None):
        """Set context for current request"""
        _request_context.request_id = request_id
        _request_context.user_id = user_id
        _request_context.metadata = metadata or {}

    def _get_request_id(self) -> Optional[str]:
        """Get request ID from context"""
        return getattr(_request_context, 'request_id', None)

    def _get_user_id(self) -> Optional[int]:
        """Get user ID from context"""
        return getattr(_request_context, 'user_id', None)

    @contextmanager
    def request_context(self, request_id: str, user_id: Optional[int] = None):
        """Context manager for request lifecycle"""
        self.set_request_context(request_id, user_id)
        try:
            yield
        finally:
            # Clean up context
            if hasattr(_request_context, 'request_id'):
                delattr(_request_context, 'request_id')
            if hasattr(_request_context, 'user_id'):
                delattr(_request_context, 'user_id')


# Global logger instance
_logger: Optional[StructuredLogger] = None


def get_logger() -> StructuredLogger:
    """Get or create global logger"""
    global _logger
    if _logger is None:
        _logger = StructuredLogger()
    return _logger


# Convenience functions for common logging patterns

def log_user_action(
    category: LogCategory,
    action: str,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    status: str = "success"
):
    """Log a user action"""
    return get_logger().log_action(category, action, user_id, details, status)


def log_error(
    category: LogCategory,
    error: Exception,
    user_id: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None
):
    """Log an error"""
    return get_logger().log_error(category, error, user_id, context)


def log_api_call(
    service: str,
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float
):
    """Log API call"""
    return get_logger().log_api_call(service, endpoint, method, status_code, duration_ms)


def log_llm_call(
    provider: str,
    model: str,
    tokens_used: int,
    duration_ms: float,
    success: bool = True,
    error: Optional[str] = None
):
    """Log LLM call"""
    return get_logger().log_llm_call(provider, model, tokens_used, duration_ms, success, error)
