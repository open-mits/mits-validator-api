"""Security utilities including rate limiting and input sanitation."""

import re
from collections.abc import Callable

from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from app.config import settings


def get_limiter() -> Limiter:
    """Create and configure rate limiter instance."""
    return Limiter(
        key_func=get_remote_address,
        default_limits=[settings.rate_limit] if settings.enable_rate_limiting else [],
        enabled=settings.enable_rate_limiting,
    )


# Global limiter instance
limiter = get_limiter()


def get_rate_limit_exceeded_handler() -> Callable:
    """Return the rate limit exceeded handler."""
    return _rate_limit_exceeded_handler


def sanitize_xml_input(xml_text: str) -> str:
    """
    Sanitize XML input by removing potentially harmful content.

    - Removes UTF-8 BOM if present
    - Strips leading/trailing whitespace
    - Validates character ranges (XML 1.0 legal characters)

    Args:
        xml_text: Raw XML text input

    Returns:
        Sanitized XML text

    Raises:
        ValueError: If input contains illegal XML 1.0 characters
    """
    # Remove UTF-8 BOM
    if xml_text.startswith("\ufeff"):
        xml_text = xml_text[1:]

    # Strip whitespace
    xml_text = xml_text.strip()

    # Check for illegal XML 1.0 characters
    # Legal: #x9 | #xA | #xD | [#x20-#xD7FF] | [#xE000-#xFFFD] | [#x10000-#x10FFFF]
    illegal_pattern = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x84\x86-\x9F\uFDD0-\uFDEF]")

    if illegal_pattern.search(xml_text):
        raise ValueError("Input contains illegal XML 1.0 control characters")

    return xml_text


def validate_content_type(request: Request) -> bool:
    """
    Validate that request has acceptable Content-Type for XML.

    Args:
        request: FastAPI request object

    Returns:
        True if content type is valid
    """
    content_type = request.headers.get("content-type", "").lower()

    accepted_types = [
        "application/xml",
        "text/xml",
    ]

    return any(accepted in content_type for accepted in accepted_types)
