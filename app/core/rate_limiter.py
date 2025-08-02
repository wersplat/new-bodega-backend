"""
Rate limiting configuration for the API endpoints.
Uses Redis as the storage backend for distributed rate limiting.
"""
from typing import List, Optional, Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import redis.asyncio as redis
from app.core.config import settings

# Initialize Redis connection
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    health_check_interval=30
)

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

# Initialize rate limiter
limiter = Limiter(
    key_func=get_identifier,
    storage_uri=settings.REDIS_URL,
    headers_enabled=True
)

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
    Get the rate limiter instance with Redis storage.
    """
    return limiter

def get_rate_limit_middleware() -> dict:
    """
    Get rate limit middleware configuration.
    """
    return {
        "key_func": get_identifier,
        "storage_uri": settings.REDIS_URL,
        "enabled": not settings.DEBUG  # Disable in debug mode
    }
