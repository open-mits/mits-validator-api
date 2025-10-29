"""
Validation service that orchestrates multiple validators.

Supports multiple validation strategies:
- Basic XML well-formedness validation
- MITS 5.0 comprehensive validation
"""

from app.security import sanitize_xml_input
from app.validators.mits import validate_mits_document
from app.validators.xml_basic import is_valid_xml


def validate(xml_text: str, validation_type: str = "mits5") -> dict[str, list[str] | bool]:
    """
    Orchestrate XML validation through multiple validators.

    This service acts as the main entry point for validation logic. It:
    1. Sanitizes and normalizes input
    2. Runs the appropriate validator based on validation_type
    3. Returns unified validation results

    Args:
        xml_text: Raw XML content to validate
        validation_type: Type of validation to perform:
                        - "basic": Basic XML well-formedness only
                        - "mits5": MITS 5.0 comprehensive validation (default)

    Returns:
        Dictionary with keys:
        - valid: bool indicating overall validation status
        - errors: list of error messages
        - warnings: list of warning messages
        - info: list of informational messages

    Example:
        >>> validate("<root><item>test</item></root>", "basic")
        {'valid': True, 'errors': [], 'warnings': [], 'info': []}

        >>> validate("<PhysicalProperty>...</PhysicalProperty>", "mits5")
        {'valid': True, 'errors': [], 'warnings': [], 'info': []}
    """
    errors: list[str] = []
    warnings: list[str] = []
    info: list[str] = []

    # Step 1: Sanitize input
    try:
        sanitized_xml = sanitize_xml_input(xml_text)
    except ValueError as e:
        errors.append(f"Input sanitation failed: {str(e)}")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "info": info,
        }

    # Step 2: Check basic length constraints
    if len(sanitized_xml) == 0:
        errors.append("XML content is empty")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "info": info,
        }

    # Step 3: Run appropriate validator based on validation_type
    if validation_type == "mits5":
        # MITS 5.0 comprehensive validation
        result = validate_mits_document(sanitized_xml)
        return result
    else:
        # Basic XML well-formedness validation
        xml_valid = is_valid_xml(sanitized_xml)

        if not xml_valid:
            errors.append("Invalid XML")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "info": info,
        }
