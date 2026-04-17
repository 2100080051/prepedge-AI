"""
Request Tracking Middleware
Adds request ID to all requests for debugging and correlation
"""

import uuid
import logging
from fastapi import Request
from contextvars import ContextVar
from typing import Optional, Callable
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable to store request ID
request_id_context: ContextVar[Optional[str]] = ContextVar('request_id', default=None)

logger = logging.getLogger(__name__)


def get_request_id() -> str:
    """Get current request ID from context"""
    request_id = request_id_context.get()
    if request_id is None:
        request_id = str(uuid.uuid4())
    return request_id


def set_request_id(request_id: str):
    """Set request ID in context"""
    request_id_context.set(request_id)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add request ID to all requests"""
    
    async def dispatch(self, request: Request, call_next: Callable):
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        
        # Set in context
        set_request_id(request_id)
        
        # Add to request state for access in endpoints
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response

