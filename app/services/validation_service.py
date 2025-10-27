"""Validation service that orchestrates multiple validators."""

from app.security import sanitize_xml_input
from app.validators.xml_basic import is_valid_xml


def validate(xml_text: str) -> dict[str, list[str] | bool]:
    """
    Orchestrate XML validation through multiple validators.

    This service acts as the main entry point for validation logic. It:
    1. Sanitizes and normalizes input
    2. Runs validators in sequence
    3. Aggregates results into a unified response

    Future validators can be added to this pipeline by:
    - Creating a new module in app/validators/
    - Importing and calling it here
    - Aggregating its results with existing validators

    Args:
        xml_text: Raw XML content to validate

    Returns:
        Dictionary with keys:
        - valid: bool indicating overall validation status
        - errors: list of error messages
        - warnings: list of warning messages
        - info: list of informational messages

    Example:
        >>> validate("<root><item>test</item></root>")
        {'valid': True, 'errors': [], 'warnings': [], 'info': []}

        >>> validate("<root><unclosed>")
        {'valid': False, 'errors': ['Invalid XML'], 'warnings': [], 'info': []}
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

    # Step 3: Run XML well-formedness validator
    # This is the primary validator for the initial implementation
    xml_valid = is_valid_xml(sanitized_xml)

    if not xml_valid:
        errors.append("Invalid XML")

    # Step 4: Future validators would be called here
    # Example (for future extension):
    # from app.validators.schema_validator import validate_schema
    # schema_result = validate_schema(sanitized_xml)
    # if not schema_result.valid:
    #     errors.extend(schema_result.errors)
    #     warnings.extend(schema_result.warnings)

    # Step 5: Determine overall validity
    # Valid only if no errors were found
    valid = len(errors) == 0

    return {
        "valid": valid,
        "errors": errors,
        "warnings": warnings,
        "info": info,
    }
