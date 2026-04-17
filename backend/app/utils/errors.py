"""
Standardized Error Handling & Response Formatting
Unified error responses across all endpoints
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any
from pydantic import BaseModel
import logging
import uuid

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response format"""
    error_code: str
    message: str
    detail: Optional[str] = None
    request_id: Optional[str] = None
    status_code: int


class AppException(HTTPException):
    """Base application exception with standardized format"""
    
    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        detail: Optional[str] = None,
        request_id: Optional[str] = None,
    ):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.detail = detail
        self.request_id = request_id or str(uuid.uuid4())
        
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "detail": detail,
                "request_id": self.request_id,
            }
        )


# ============================================================================
# Predefined Exceptions for Common Scenarios
# ============================================================================

class AuthenticationError(AppException):
    """Invalid credentials or missing authentication"""
    def __init__(self, message: str = "Authentication failed", detail: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_FAILED",
            message=message,
            detail=detail,
            request_id=request_id,
        )


class InvalidCredentialsError(AppException):
    """Invalid email or password"""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="INVALID_CREDENTIALS",
            message="Invalid email or password",
            request_id=request_id,
        )


class EmailNotVerifiedError(AppException):
    """Email verification required"""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="EMAIL_NOT_VERIFIED",
            message="Email verification required",
            detail="Please check your email for verification link",
            request_id=request_id,
        )


class AccountDeactivatedError(AppException):
    """Account has been deactivated"""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="ACCOUNT_DEACTIVATED",
            message="Account has been deactivated",
            request_id=request_id,
        )


class ValidationError(AppException):
    """Input validation error"""
    def __init__(self, message: str, detail: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="VALIDATION_ERROR",
            message=message,
            detail=detail,
            request_id=request_id,
        )


class ResourceNotFoundError(AppException):
    """Resource not found (404)"""
    def __init__(self, resource: str = "Resource", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            message=f"{resource} not found",
            request_id=request_id,
        )


class ConflictError(AppException):
    """Resource conflict (duplicate email, username, etc.)"""
    def __init__(self, message: str, detail: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="CONFLICT",
            message=message,
            detail=detail,
            request_id=request_id,
        )


class DuplicateEmailError(AppException):
    """Email already registered"""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_EMAIL",
            message="Email already registered",
            detail="Try login or use forgot password",
            request_id=request_id,
        )


class DuplicateUsernameError(AppException):
    """Username already taken"""
    def __init__(self, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_USERNAME",
            message="Username already taken",
            detail="Choose a different username",
            request_id=request_id,
        )


class InternalServerError(AppException):
    """Internal server error (500)"""
    def __init__(self, message: str = "Internal server error", detail: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR",
            message=message,
            detail=detail,
            request_id=request_id,
        )


class DatabaseError(AppException):
    """Database operation error"""
    def __init__(self, message: str = "Database error", detail: Optional[str] = None, request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            message=message,
            detail=detail,
            request_id=request_id,
        )


class ExternalServiceError(AppException):
    """External service (email, payment, etc.) error"""
    def __init__(self, service: str = "External service", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="EXTERNAL_SERVICE_ERROR",
            message=f"{service} is temporarily unavailable",
            detail="Please try again later",
            request_id=request_id,
        )


class SecurityError(AppException):
    """Security violation (SQL injection, XSS, etc.)"""
    def __init__(self, message: str = "Invalid request", request_id: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="SECURITY_ERROR",
            message=message,
            detail="Your request contains invalid characters",
            request_id=request_id,
        )


# ============================================================================
# Error Handler Utility
# ============================================================================

def log_error(error: Exception, request_id: str = None, context: Dict[str, Any] = None):
    """Log error with context"""
    if request_id is None:
        request_id = str(uuid.uuid4())
    
    extra = {
        "request_id": request_id,
        "error_type": type(error).__name__,
    }
    
    if context:
        extra.update(context)
    
    logger.error(
        f"Error occurred: {str(error)}",
        extra=extra,
        exc_info=True
    )
    
    return request_id
