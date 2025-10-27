"""API v5.0 router for MTS5 (RETTC) validation endpoints."""

import logging

import anyio
from fastapi import APIRouter, HTTPException, Request, status

from app.config import settings
from app.models.dto import ValidateRequestJSON, ValidateResponse
from app.security import limiter, validate_content_type
from app.services.validation_service import validate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v5.0", tags=["validation"])


@router.post(
    "/validate",
    response_model=ValidateResponse,
    status_code=status.HTTP_200_OK,
    summary="Validate MTS5 (RETTC) XML payload",
    description="""
    Validate an MTS5 (RETTC) XML document for well-formedness and compliance.

    Accepts raw XML body with Content-Type: application/xml or text/xml

    Returns validation results with status, errors, warnings, and informational messages.
    
    **Always returns 200 OK** with the validation result structure, even for invalid requests.

    Security features:
    - Safe XML parsing with defusedxml (XXE and entity expansion protection)
    - Request body size limits
    - Rate limiting per IP address
    - Timeout protection for parsing operations
    """,
    responses={
        200: {
            "description": "Validation completed successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "valid_xml": {
                            "summary": "Valid XML",
                            "value": {
                                "valid": True,
                                "errors": [],
                                "warnings": [],
                                "info": [],
                            },
                        },
                        "invalid_xml": {
                            "summary": "Invalid XML",
                            "value": {
                                "valid": False,
                                "errors": ["Invalid XML"],
                                "warnings": [],
                                "info": [],
                            },
                        },
                        "empty_body": {
                            "summary": "Empty Body",
                            "value": {
                                "valid": False,
                                "errors": ["Request body is empty"],
                                "warnings": [],
                                "info": [],
                            },
                        },
                        "wrong_content_type": {
                            "summary": "Wrong Content-Type",
                            "value": {
                                "valid": False,
                                "errors": ["Invalid Content-Type. Expected application/xml or text/xml"],
                                "warnings": [],
                                "info": [],
                            },
                        },
                    }
                }
            },
        },
        413: {"description": "Request body too large"},
        429: {"description": "Rate limit exceeded"},
    },
)
@limiter.limit(settings.rate_limit)
async def validate_xml(request: Request) -> ValidateResponse:
    """
    Validate XML payload endpoint.

    Accepts raw XML body with Content-Type: application/xml or text/xml.
    Always returns ValidateResponse structure, even for errors.

    Args:
        request: FastAPI request object

    Returns:
        ValidateResponse with validation results (always 200 OK)
    """
    # Check content type
    content_type = request.headers.get("content-type", "").lower()
    if not any(ct in content_type for ct in ["application/xml", "text/xml"]):
        return ValidateResponse(
            valid=False,
            errors=["Invalid Content-Type. Expected application/xml or text/xml"],
            warnings=[],
            info=[],
        )

    # Extract XML content
    try:
        body_bytes = await request.body()
        xml_text = body_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return ValidateResponse(
            valid=False,
            errors=["Invalid UTF-8 encoding in request body"],
            warnings=[],
            info=[],
        )
    except Exception as e:
        logger.error(f"Error reading request body: {str(e)}")
        return ValidateResponse(
            valid=False,
            errors=["Failed to read request body"],
            warnings=[],
            info=[],
        )

    # Check for empty body
    if not xml_text.strip():
        return ValidateResponse(
            valid=False,
            errors=["Request body is empty"],
            warnings=[],
            info=[],
        )

    # Perform validation with timeout protection
    try:
        with anyio.fail_after(settings.request_timeout_seconds):
            result: dict[str, list[str] | bool] = validate(xml_text)

        return ValidateResponse(
            valid=bool(result["valid"]),
            errors=list(result["errors"]) if isinstance(result["errors"], list) else [],
            warnings=list(result["warnings"]) if isinstance(result["warnings"], list) else [],
            info=list(result["info"]) if isinstance(result["info"], list) else [],
        )

    except TimeoutError:
        return ValidateResponse(
            valid=False,
            errors=[f"Validation timed out after {settings.request_timeout_seconds} seconds"],
            warnings=[],
            info=[],
        )
    except Exception as e:
        logger.error(f"Unexpected error during validation: {str(e)}")
        return ValidateResponse(
            valid=False,
            errors=["An unexpected error occurred during validation"],
            warnings=[],
            info=[],
        )
