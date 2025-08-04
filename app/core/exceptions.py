"""
Custom exceptions and error handling for the NBA 2K Global Rankings API
"""

from typing import Any, Dict, Optional, Union
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import structlog

logger = structlog.get_logger(__name__)

class NBA2KAPIException(Exception):
    """Base exception for NBA 2K API"""
    
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationException(NBA2KAPIException):
    """Raised when input validation fails"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )

class AuthenticationException(NBA2KAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )

class AuthorizationException(NBA2KAPIException):
    """Raised when authorization fails"""
    
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )

class ResourceNotFoundException(NBA2KAPIException):
    """Raised when a requested resource is not found"""
    
    def __init__(self, resource_type: str, resource_id: Union[str, int]):
        super().__init__(
            message=f"{resource_type} with id {resource_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource_type": resource_type, "resource_id": str(resource_id)}
        )

class ResourceConflictException(NBA2KAPIException):
    """Raised when there's a conflict with an existing resource"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code="RESOURCE_CONFLICT",
            details=details
        )

class RateLimitException(NBA2KAPIException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, retry_after: int = 60):
        super().__init__(
            message="Rate limit exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )

class DatabaseException(NBA2KAPIException):
    """Raised when database operations fail"""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )

class ExternalServiceException(NBA2KAPIException):
    """Raised when external service calls fail"""
    
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service} service error: {message}",
            status_code=status.HTTP_502_BAD_GATEWAY,
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service, **details} if details else {"service": service}
        )

def create_error_response(
    exception: NBA2KAPIException,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create a standardized error response"""
    
    error_data = {
        "error": {
            "code": exception.error_code,
            "message": exception.message,
            "status_code": exception.status_code
        }
    }
    
    if exception.details:
        error_data["error"]["details"] = exception.details
    
    if request_id:
        error_data["request_id"] = request_id
    
    # Log the error
    logger.error(
        "API error",
        error_code=exception.error_code,
        message=exception.message,
        status_code=exception.status_code,
        details=exception.details,
        request_id=request_id
    )
    
    return JSONResponse(
        status_code=exception.status_code,
        content=error_data
    )

def handle_validation_error(exc: ValidationError, request_id: Optional[str] = None) -> JSONResponse:
    """Handle Pydantic validation errors"""
    
    error_details = []
    for error in exc.errors():
        error_details.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    exception = ValidationException(
        message="Validation error",
        details={"errors": error_details}
    )
    
    return create_error_response(exception, request_id)

def handle_generic_exception(exc: Exception, request_id: Optional[str] = None) -> JSONResponse:
    """Handle generic exceptions"""
    
    # Log the unexpected error
    logger.error(
        "Unexpected error",
        error_type=type(exc).__name__,
        error_message=str(exc),
        request_id=request_id,
        exc_info=True
    )
    
    exception = NBA2KAPIException(
        message="An unexpected error occurred",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="INTERNAL_SERVER_ERROR"
    )
    
    return create_error_response(exception, request_id)

# Common error messages
ERROR_MESSAGES = {
    "player_not_found": "Player not found",
    "event_not_found": "Event not found",
    "team_not_found": "Team not found",
    "match_not_found": "Match not found",
    "gamertag_taken": "Gamertag is already taken",
    "invalid_credentials": "Invalid email or password",
    "token_expired": "Access token has expired",
    "insufficient_permissions": "Insufficient permissions for this operation",
    "rate_limit_exceeded": "Rate limit exceeded. Please try again later",
    "database_connection_failed": "Database connection failed",
    "external_service_unavailable": "External service is temporarily unavailable"
}