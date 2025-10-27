"""FastAPI application factory and main entry point."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.api import v5
from app.config import settings
from app.errors import (
    generic_exception_handler,
    validation_exception_handler,
)
from app.middleware import BodySizeLimitMiddleware, LoggingMiddleware, RequestIDMiddleware
from app.security import limiter

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Production-grade API for validating MTS5 (RETTC) XML payloads",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url="/redoc" if settings.enable_docs else None,
        openapi_url="/openapi.json" if settings.enable_docs else None,
    )

    # Add state for rate limiter
    app.state.limiter = limiter

    # Register exception handlers
    app.add_exception_handler(Exception, generic_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RateLimitExceeded, rate_limit_handler)  # type: ignore[arg-type]

    # Add middleware (order matters - last added is executed first)
    # 1. Body size limit (earliest to reject oversized requests)
    app.add_middleware(BodySizeLimitMiddleware, max_body_size=settings.max_body_bytes)

    # 2. Request ID (for tracking)
    app.add_middleware(RequestIDMiddleware)

    # 3. Logging (uses request ID)
    app.add_middleware(LoggingMiddleware)

    # 4. CORS (if configured)
    if settings.allowed_origins_list:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.allowed_origins_list,
            allow_credentials=settings.allow_credentials,
            allow_methods=settings.allowed_methods_list,
            allow_headers=settings.allowed_headers_list,
        )

    # Include routers
    app.include_router(v5.router)

    # Health check endpoint
    @app.get(
        "/healthz",
        tags=["health"],
        summary="Health check endpoint",
        description="Returns the health status of the service",
    )
    async def health_check() -> JSONResponse:
        """Simple health check endpoint."""
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": settings.app_name,
                "version": settings.app_version,
            },
        )

    @app.get("/", include_in_schema=False)
    async def root() -> JSONResponse:
        """Root endpoint redirect."""
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Welcome to {settings.app_name}",
                "version": settings.app_version,
                "docs": "/docs" if settings.enable_docs else "Documentation disabled",
            },
        )

    return app


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Handle rate limit exceeded exceptions."""
    request_id = getattr(request.state, "request_id", None)
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "detail": str(exc.detail),
            "request_id": request_id,
        },
    )


# Create application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
