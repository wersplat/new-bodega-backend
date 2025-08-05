"""
Structured logging configuration for the NBA 2K Global Rankings backend
"""

import logging
import sys
from typing import Any, Dict
from datetime import datetime

import structlog
from structlog.stdlib import LoggerFactory


def configure_logging() -> None:
    """Configure structured logging for the application"""
    from app.core.config import settings
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.is_production else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    
    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)

def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)

class RequestLogger:
    """Context manager for logging request/response information"""
    
    def __init__(self, logger: structlog.stdlib.BoundLogger, request_id: str):
        self.logger = logger
        self.request_id = request_id
        self.start_time = None
    
    def __enter__(self):
        self.start_time = datetime.utcnow()
        self.logger.info(
            "Request started",
            request_id=self.request_id,
            timestamp=self.start_time.isoformat()
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                "Request failed",
                request_id=self.request_id,
                duration=duration,
                error_type=exc_type.__name__,
                error_message=str(exc_val),
                timestamp=datetime.utcnow().isoformat()
            )
        else:
            self.logger.info(
                "Request completed",
                request_id=self.request_id,
                duration=duration,
                timestamp=datetime.utcnow().isoformat()
            )

def log_request_info(request: Any, user_id: str = None, **kwargs) -> Dict[str, Any]:
    """Log request information with structured data"""
    logger = get_logger("api.request")
    
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "path": request.url.path,
        "query_params": dict(request.query_params),
        "headers": dict(request.headers),
        "client_ip": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
        "user_id": user_id,
        **kwargs
    }
    
    # Remove sensitive information in production
    if settings.is_production:
        request_info.pop("headers", None)
        request_info.pop("user_agent", None)
    
    logger.info("API request", **request_info)
    return request_info

def log_error(error: Exception, context: Dict[str, Any] = None) -> None:
    """Log errors with structured context"""
    logger = get_logger("api.error")
    
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error("Application error", **error_info)

# Initialize logging on module import
configure_logging()