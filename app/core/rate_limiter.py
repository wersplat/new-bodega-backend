"""
Rate limiting configuration for the API endpoints.
Uses in-memory storage for rate limiting.
"""
from typing import List, Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from app.core.config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Check if rate limiting should be disabled
DISABLE_RATE_LIMITING = os.getenv("DISABLE_RATE_LIMITING", "false").lower() == "true"

# Custom rate limit key function
def get_identifier(request: Request) -> str:
    """
    Get a unique identifier for rate limiting.
    Uses API key if provided, otherwise falls back to IP address.
    """
    # Try to get API key from headers
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    
    # Fall back to IP address
    return get_remote_address(request)

# Initialize rate limiter with in-memory storage
if DISABLE_RATE_LIMITING:
    # Create a dummy limiter that doesn't actually limit
    class DummyLimiter:
        def limit(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        
        def exempt(self, func):
            return func
    
    limiter = DummyLimiter()
    logger.info("Rate limiting disabled - using dummy limiter")
else:
    # Use in-memory storage
    limiter = Limiter(
        key_func=get_identifier,
        storage_uri="memory://",
        headers_enabled=True
    )
    logger.info("Rate limiting enabled - using in-memory storage")

# Rate limit exceeded handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Custom handler for rate limit exceeded responses.
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": f"{exc.retry_after} seconds"
        },
        headers={
            "Retry-After": str(int(exc.retry_after)),
            "X-RateLimit-Limit": str(exc.limit.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(exc.reset_at.timestamp()))
        }
    )

def get_rate_limiter() -> Limiter:
    """
    Get the rate limiter instance with in-memory storage.
    """
    return limiter

def get_rate_limit_middleware() -> dict:
    """
    Get rate limit middleware configuration.
    """
    if DISABLE_RATE_LIMITING:
        return {"enabled": False}
    
    return {
        "key_func": get_identifier,
        "storage_uri": "memory://",
        "enabled": not settings.DEBUG  # Disable in debug mode
    }
