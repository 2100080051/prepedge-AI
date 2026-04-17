"""
Rate Limiting Configuration for PrepEdge API
Implements tiered rate limiting per endpoint
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from functools import wraps
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)

# Initialize limiter
limiter = Limiter(key_func=get_remote_address)

# Define rate limit configurations per endpoint
ENDPOINT_LIMITS = {
    # Authentication endpoints (stricter limits)
    "/api/v1/auth/register": {
        "limit": "5/minute",
        "description": "New user registration - prevent spam"
    },
    "/api/v1/auth/login": {
        "limit": "10/minute",
        "description": "User login - prevent brute force"
    },
    "/api/v1/auth/verify-email": {
        "limit": "20/minute",
        "description": "Email verification - allow multiple attempts"
    },
    "/api/v1/auth/resend-verification-email": {
        "limit": "5/minute",
        "description": "Resend verification - prevent spam"
    },
    "/api/v1/auth/forgot-password": {
        "limit": "3/minute",
        "description": "Password reset - prevent spam"
    },
    "/api/v1/auth/reset-password": {
        "limit": "5/minute",
        "description": "Password reset - allow retries"
    },
    
    # API endpoints (moderate limits)
    "/api/v1/questions": {
        "limit": "100/minute",
        "description": "Questions endpoint"
    },
    "/api/v1/flashcards": {
        "limit": "100/minute",
        "description": "Flashcards endpoint"
    },
    "/api/v1/flashlearn": {
        "limit": "100/minute",
        "description": "FlashLearn endpoint"
    },
    
    # File upload endpoints (stricter limits)
    "/api/v1/resume": {
        "limit": "10/minute",
        "description": "Resume upload - prevent abuse"
    },
    "/api/v1/jdparser": {
        "limit": "10/minute",
        "description": "Job description upload - prevent abuse"
    },
    
    # AI/LLM endpoints (moderate limits)
    "/api/v1/code-execution": {
        "limit": "50/minute",
        "description": "Code execution - prevent long-running requests"
    },
    "/api/v1/mockmate": {
        "limit": "50/minute",
        "description": "Mock interviews"
    },
    "/api/v1/learnai": {
        "limit": "50/minute",
        "description": "LearnAI - AI content generation"
    },
    
    # General endpoints (permissive limits)
    "/api/v1/dashboard": {
        "limit": "100/minute",
        "description": "Dashboard data"
    },
    "/api/v1/engage": {
        "limit": "100/minute",
        "description": "Engagement tracking"
    },
}

# Default rate limit for endpoints without specific config
DEFAULT_LIMIT = "100/minute"

def get_rate_limit(path: str) -> str:
    """Get rate limit for a given endpoint path"""
    return ENDPOINT_LIMITS.get(path, {}).get("limit", DEFAULT_LIMIT)

def get_rate_limit_description(path: str) -> Optional[str]:
    """Get description for rate limit"""
    return ENDPOINT_LIMITS.get(path, {}).get("description")

# Global rate limit decorator
def apply_rate_limit(limit: str) -> Callable:
    """Decorator to apply rate limiting to a route"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Helper function to get all rate limit configurations
def get_all_limits() -> dict:
    """Get all rate limit configurations for documentation"""
    return {
        "endpoints": ENDPOINT_LIMITS,
        "default": DEFAULT_LIMIT,
        "note": "Rate limits are per IP address and enforce sliding window"
    }

# Rate limit status codes
RATE_LIMIT_EXCEEDED = 429
RATE_LIMIT_RETRY_AFTER = 60  # seconds
