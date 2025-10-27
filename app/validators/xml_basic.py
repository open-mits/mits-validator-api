"""Basic XML well-formedness validator using defusedxml."""

from typing import Any
from xml.etree.ElementTree import ParseError

import defusedxml.ElementTree as ET

from app.config import settings


def is_valid_xml(xml_text: str) -> bool:
    """
    Validate XML well-formedness using defusedxml for safe parsing.

    This function checks if the provided XML text is well-formed by attempting
    to parse it with defusedxml, which protects against:
    - XML External Entity (XXE) attacks
    - Billion Laughs (entity expansion) attacks
    - DTD retrieval
    - Quadratic blowup attacks

    Args:
        xml_text: XML content as string

    Returns:
        True if XML is well-formed, False otherwise

    Note:
        This validator only checks well-formedness. Additional semantic
        validation rules can be added by creating new validators in this package.
    """
    if not xml_text or not xml_text.strip():
        return False

    try:
        # defusedxml.ElementTree.fromstring is safer than standard library
        # It automatically disables:
        # - DTD processing
        # - External entity expansion
        # - Entity references beyond basic XML entities
        root = ET.fromstring(xml_text)

        # Additional safety check: verify depth doesn't exceed configured limit
        if settings.enable_xml_validation:
            max_depth = _get_xml_depth(root)
            if max_depth > settings.max_xml_depth:
                return False

        return True

    except ParseError:
        # XML is not well-formed
        return False
    except Exception:
        # Catch DTDForbidden, EntitiesForbidden, ExternalReferenceForbidden,
        # NotSupportedError, and any other parsing errors safely
        # defusedxml raises these exceptions to prevent XXE attacks
        return False


def _get_xml_depth(element: Any, current_depth: int = 1) -> int:
    """
    Calculate the maximum depth of an XML element tree.

    Args:
        element: Root element to measure
        current_depth: Current depth level (for recursion)

    Returns:
        Maximum depth of the tree
    """
    if not list(element):  # No children
        return current_depth

    return max(_get_xml_depth(child, current_depth + 1) for child in element)
