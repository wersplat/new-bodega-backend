"""
Rate limiting configuration for the API endpoints.
Uses Redis in production if available, otherwise in-memory storage.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

DISABLE_RATE_LIMITING = bool(getattr(settings, "DISABLE_RATE_LIMITING", False))

def get_identifier(request: Request) -> str:
    """Identify a client by API key header or remote address."""
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    return get_remote_address(request)

if DISABLE_RATE_LIMITING:
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
    storage_uri = settings.rate_limit_storage_uri
    limiter = Limiter(
        key_func=get_identifier,
        storage_uri=storage_uri,
        headers_enabled=True,
    )
    logger.info(f"Rate limiting enabled - storage: {storage_uri}")

async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "retry_after": f"{exc.retry_after} seconds",
        },
        headers={
            "Retry-After": str(int(exc.retry_after)),
            "X-RateLimit-Limit": str(exc.limit.limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(exc.reset_at.timestamp())),
        },
    )

def is_rate_limiting_enabled() -> bool:
    return not DISABLE_RATE_LIMITING
