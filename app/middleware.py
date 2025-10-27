"""Middleware for request processing, logging, and size limits."""

import json
import logging
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.errors import BodyTooLargeError

# Configure JSON logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(message)s",
)

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add a unique request ID to each request."""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        """Add request ID to request state and response headers."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for JSON-formatted access logging."""

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        """Log request and response details in JSON format."""
        start_time = time.time()
        request_id = getattr(request.state, "request_id", "unknown")

        # Log request
        logger.info(
            json.dumps(
                {
                    "event": "request_started",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "client_host": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                }
            )
        )

        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            logger.error(
                json.dumps(
                    {
                        "event": "request_error",
                        "request_id": request_id,
                        "method": request.method,
                        "path": request.url.path,
                        "error": str(exc),
                        "error_type": type(exc).__name__,
                        "duration_ms": (time.time() - start_time) * 1000,
                    }
                )
            )
            raise

        # Log response
        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            json.dumps(
                {
                    "event": "request_completed",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration_ms, 2),
                }
            )
        )

        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request body size limits."""

    def __init__(self, app: Callable[..., Any], max_body_size: int) -> None:
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Any:
        """Check Content-Length header before processing request body."""
        content_length = request.headers.get("content-length")

        if content_length:
            content_length_int = int(content_length)
            if content_length_int > self.max_body_size:
                raise BodyTooLargeError(max_size=self.max_body_size)

        return await call_next(request)
