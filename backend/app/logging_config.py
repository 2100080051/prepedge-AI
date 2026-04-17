"""
Production logging and monitoring setup.
Integrates with multiple logging backends (file, syslog, monitoring).
"""

import logging
import logging.config
import logging.handlers
from pathlib import Path
from datetime import datetime
import json
from app.config import settings

# Create logs directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# JSON Formatter for structured logging
class JSONFormatter(logging.Formatter):
    """Format logs as JSON for easier parsing."""
    
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add custom fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "duration"):
            log_data["duration_ms"] = record.duration
        
        return json.dumps(log_data)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": JSONFormatter,
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(funcName)s() - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "file_json": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(LOG_DIR / "app.json.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "error.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 10,
        },
        "celery_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "json",
            "filename": str(LOG_DIR / "celery.json.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
    },
    "loggers": {
        # Root logger
        "": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console", "file", "error_file"],
        },
        # Application loggers
        "app": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["console", "file", "file_json", "error_file"],
            "propagate": False,
        },
        # Celery logging
        "celery": {
            "level": "INFO",
            "handlers": ["console", "celery_file"],
            "propagate": False,
        },
        "celery.task": {
            "level": "INFO",
            "handlers": ["console", "celery_file"],
            "propagate": False,
        },
        # SQLAlchemy logging (only in debug)
        "sqlalchemy.engine": {
            "level": "DEBUG" if settings.DEBUG else "INFO",
            "handlers": ["file"],
            "propagate": False,
        },
        # FastAPI/Starlette logging
        "fastapi": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        "uvicorn": {
            "level": "INFO",
            "handlers": ["console", "file"],
            "propagate": False,
        },
        # External library loggers (silence noisy ones)
        "urllib3": {
            "level": "WARNING",
            "handlers": ["file"],
            "propagate": False,
        },
        "openai": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False,
        },
        "langchain": {
            "level": "INFO",
            "handlers": ["file"],
            "propagate": False,
        },
    },
}


def setup_logging():
    """Initialize logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized - Environment: {settings.ENVIRONMENT}")


# Request context for logging
class RequestContextFilter(logging.Filter):
    """Add request context to log records."""
    
    def filter(self, record):
        # This will be populated by middleware
        record.request_id = getattr(record, "request_id", "N/A")
        record.user_id = getattr(record, "user_id", "N/A")
        return True


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    logger = logging.getLogger(name)
    logger.addFilter(RequestContextFilter())
    return logger


# Initialize on import
setup_logging()
