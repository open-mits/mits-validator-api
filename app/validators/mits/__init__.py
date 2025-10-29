"""
MITS 5.0 Validators

This package contains comprehensive validators for MITS 5.0 (Rental Options & Fees) XML documents.
Validators are organized into logical sections matching the specification document.

Usage:
    from app.validators.mits import validate_mits_document
    
    result = validate_mits_document(xml_text)
    if not result.valid:
        for error in result.errors:
            print(f"Error: {error}")
"""

from app.validators.mits.orchestrator import validate_mits_document

__all__ = ["validate_mits_document"]

