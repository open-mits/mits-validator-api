"""Pydantic models for request and response validation."""

from pydantic import BaseModel, Field, field_validator


class ValidateRequestJSON(BaseModel):
    """Request model for JSON-wrapped XML validation."""

    xml: str = Field(
        ...,
        min_length=1,
        description="XML content to validate",
        examples=["<root><item>value</item></root>"],
    )

    @field_validator("xml")
    @classmethod
    def xml_not_empty(cls, v: str) -> str:
        """Ensure XML content is not just whitespace."""
        if not v.strip():
            raise ValueError("XML content cannot be empty or whitespace only")
        return v


class ValidateResponse(BaseModel):
    """Response model for validation results."""

    valid: bool = Field(
        ...,
        description="Whether the XML document is valid",
    )
    errors: list[str] = Field(
        default_factory=list,
        description="List of validation error messages",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="List of validation warnings",
    )
    info: list[str] = Field(
        default_factory=list,
        description="List of informational messages",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                    "info": [],
                },
                {
                    "valid": False,
                    "errors": ["Invalid XML: mismatched tag"],
                    "warnings": [],
                    "info": [],
                },
            ]
        }
    }
