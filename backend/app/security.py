"""
Security Module - Comprehensive security hardening for PrepEdge
Includes rate limiting, input validation, security headers, and logging
"""

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging
import re
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Security logging
security_logger = logging.getLogger("security")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '%(asctime)s - [SECURITY] - %(levelname)s - %(message)s'
))
security_logger.addHandler(handler)
security_logger.setLevel(logging.WARNING)

# ============================================================================
# INPUT VALIDATION
# ============================================================================

class InputValidator:
    """Validate and sanitize user inputs"""
    
    # Patterns for validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_SPECIAL = True
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email or len(email) > 254:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_password(password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < InputValidator.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {InputValidator.PASSWORD_MIN_LENGTH} characters"
        
        if len(password) > 128:
            return False, "Password is too long (max 128 characters)"
        
        # Check for required character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit):
            return False, "Password must contain uppercase, lowercase, and numbers"
        
        if InputValidator.PASSWORD_REQUIRE_SPECIAL and not has_special:
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username:
            return False
        return bool(InputValidator.USERNAME_PATTERN.match(username))
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        """Sanitize string input"""
        if not value:
            return ""
        
        # Limit length
        value = value[:max_length]
        
        # Remove null bytes (SQL injection vector)
        value = value.replace('\x00', '')
        
        # Strip whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Detect potential SQL injection attempts
        Returns True if suspicious, False if safe
        """
        dangerous_patterns = [
            r"('|(\")|(--)|(;)|(--|#)|(\*)|(\b(UNION|SELECT|DROP|DELETE|INSERT|UPDATE)\b))",
        ]
        
        value_upper = value.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_upper, re.IGNORECASE):
                return True  # Suspicious
        
        return False  # Safe
    
    @staticmethod
    def check_xss_injection(value: str) -> bool:
        """
        Detect potential XSS attacks
        Returns True if suspicious, False if safe
        """
        xss_patterns = [
            r'<script',
            r'javascript:',
            r'onerror=',
            r'onload=',
            r'onclick=',
            r'<iframe',
            r'<object',
            r'<embed',
        ]
        
        value_lower = value.lower()
        for pattern in xss_patterns:
            if pattern in value_lower:
                return True  # Suspicious
        
        return False  # Safe

# ============================================================================
# RATE LIMITING
# ============================================================================

RATE_LIMITS = {
    "auth_register": "5/minute",      # 5 registrations per minute
    "auth_login": "10/minute",         # 10 login attempts per minute
    "auth_forgot_password": "3/minute", # 3 password resets per minute
    "api_general": "100/minute",       # 100 general API calls per minute
}

# ============================================================================
# SECURITY HEADERS
# ============================================================================

def add_security_headers(app: FastAPI):
    """Add security headers to all responses"""
    
    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        response = await call_next(request)
        
        # HSTS (HTTP Strict Transport Security)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Clickjacking protection
        response.headers["X-Frame-Options"] = "DENY"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'"
        )
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=()"
        )
        
        return response

# ============================================================================
# SECURITY LOGGING
# ============================================================================

class SecurityEventLogger:
    """Log security-relevant events"""
    
    @staticmethod
    def log_failed_login(email: str, ip: str, reason: str = "Invalid credentials"):
        """Log failed login attempt"""
        security_logger.warning(
            f"Failed login attempt | Email: {email} | IP: {ip} | Reason: {reason}"
        )
    
    @staticmethod
    def log_rate_limit_exceeded(endpoint: str, ip: str):
        """Log rate limit exceeded"""
        security_logger.warning(
            f"Rate limit exceeded | Endpoint: {endpoint} | IP: {ip}"
        )
    
    @staticmethod
    def log_sql_injection_attempt(endpoint: str, ip: str, payload: str):
        """Log SQL injection attempt"""
        security_logger.critical(
            f"SQL injection attempt detected | Endpoint: {endpoint} | IP: {ip} | Payload: {payload[:100]}"
        )
    
    @staticmethod
    def log_xss_attempt(endpoint: str, ip: str, payload: str):
        """Log XSS attempt"""
        security_logger.critical(
            f"XSS attempt detected | Endpoint: {endpoint} | IP: {ip} | Payload: {payload[:100]}"
        )
    
    @staticmethod
    def log_suspicious_activity(event_type: str, details: dict, ip: str):
        """Log suspicious activity"""
        security_logger.warning(
            f"Suspicious activity | Type: {event_type} | IP: {ip} | Details: {details}"
        )
    
    @staticmethod
    def log_successful_event(event: str, user_id: Optional[int] = None, ip: str = ""):
        """Log security-relevant successful events"""
        security_logger.info(
            f"Security event | Event: {event} | User ID: {user_id} | IP: {ip}"
        )

# ============================================================================
# RATE LIMIT ERROR HANDLER
# ============================================================================

def rate_limit_error_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit errors"""
    ip = request.client.host if request.client else "unknown"
    endpoint = request.url.path
    
    SecurityEventLogger.log_rate_limit_exceeded(endpoint, ip)
    
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Too many requests. Please try again later.",
            "retry_after": "60 seconds"
        }
    )

# ============================================================================
# SECURITY EXCEPTION HANDLERS
# ============================================================================

def setup_security_handlers(app: FastAPI):
    """Setup security exception handlers"""
    app.add_exception_handler(RateLimitExceeded, rate_limit_error_handler)

# ============================================================================
# UTILITIES
# ============================================================================

def get_client_ip(request: Request) -> str:
    """Get client IP address, accounting for proxies"""
    if request.client:
        return request.client.host
    
    # Check for proxy headers
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    
    if "cf-connecting-ip" in request.headers:  # Cloudflare
        return request.headers["cf-connecting-ip"]
    
    return "unknown"
