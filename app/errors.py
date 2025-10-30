"""Custom exceptions and error handlers."""

from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ValidationError(Exception):
    """Base exception for validation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class XMLParseError(ValidationError):
    """Exception raised when XML parsing fails."""

    pass


class BodyTooLargeError(HTTPException):
    """Exception raised when request body exceeds size limit."""

    def __init__(self, max_size: int) -> None:
        super().__init__(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Request body too large. Maximum allowed size: {max_size} bytes",
        )


class TimeoutError(HTTPException):
    """Exception raised when operation exceeds timeout."""

    def __init__(self, operation: str, timeout_seconds: int) -> None:
        super().__init__(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"{operation} timed out after {timeout_seconds} seconds",
        )


def create_error_response(
    status_code: int,
    message: str,
    details: dict[str, Any] | None = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Create a standardized error response."""
    content = {
        "error": message,
        "status_code": status_code,
    }
    if details:
        content["details"] = details
    if request_id:
        content["request_id"] = request_id

    return JSONResponse(status_code=status_code, content=content)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTPException and return JSON response."""
    request_id = getattr(request.state, "request_id", None)
    return create_error_response(
        status_code=exc.status_code,
        message=exc.detail if isinstance(exc.detail, str) else str(exc.detail),
        request_id=request_id,
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors and return JSON response."""
    request_id = getattr(request.state, "request_id", None)
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        details={"errors": exc.errors()},
        request_id=request_id,
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions and return JSON response without leaking details."""
    request_id = getattr(request.state, "request_id", None)

    # Log the actual error server-side (would be picked up by logging middleware)
    # but don't expose stack traces to the client
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
        request_id=request_id,
    )
