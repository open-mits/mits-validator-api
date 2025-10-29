"""
XML Structure Validator

Validates fundamental XML structure and Property identity requirements.
These are critical checks that must pass before proceeding with detailed validation.
"""

import re
from typing import Set

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class XmlStructureValidator(BaseValidator):
    """
    Validator for XML Structure.

    Rules:
        - xml_wellformed: XML is well-formed (no parse errors) - handled by parser
        - xml_encoding_utf8: Encoding is UTF-8 (or declared and decodes successfully) - handled by parser
        - root_is_physical_property: Single root element is <PhysicalProperty>
        - property_exists: <PhysicalProperty> contains ≥1 <Property>
        - property_has_id: Every <Property> has non-empty @IDValue
        - property_id_unique: @IDValue values are unique across all <Property> elements
    """

    section_name = "XML Structure"
    section_id = "xml_structure"

    def validate(self) -> ValidationResult:
        """
        Execute XML structure validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Rule: root_is_physical_property
        if self.root.tag != "PhysicalProperty":
            self.result.add_error(
                rule_id="root_is_physical_property",
                message=f"Root element must be <PhysicalProperty>, found <{self.root.tag}>",
                element_path=f"/{self.root.tag}",
            )
            return self.result

        # Rule: property_exists
        properties = self.root.findall("Property")
        if not properties:
            self.result.add_error(
                rule_id="property_exists",
                message="<PhysicalProperty> must contain at least one <Property> element",
                element_path="/PhysicalProperty",
            )
            return self.result

        # Rules: property_has_id & property_id_unique
        property_ids: Set[str] = set()

        for idx, prop in enumerate(properties, start=1):
            id_value = prop.get("IDValue", "").strip()

            # Rule: property_has_id
            if not id_value:
                self.result.add_error(
                    rule_id="property_has_id",
                    message=f"<Property> element #{idx} missing or has empty @IDValue attribute",
                    element_path=f"/PhysicalProperty/Property[{idx}]",
                )
                continue

            # Rule: property_id_unique
            if id_value in property_ids:
                self.result.add_error(
                    rule_id="property_id_unique",
                    message=f"Duplicate Property @IDValue '{id_value}' found. "
                    f"Property IDs must be unique across all <Property> elements",
                    element_path=f"/PhysicalProperty/Property[@IDValue='{id_value}']",
                    details={"duplicate_id": id_value},
                )
            else:
                property_ids.add(id_value)

        return self.result


def validate_xml_wellformed(xml_text: str) -> ValidationResult:
    """
    Validate XML well-formedness and encoding.

    This function is called before creating the validator instance since
    it needs to handle parsing errors.

    Args:
        xml_text: Raw XML text to validate

    Returns:
        ValidationResult with any parsing errors
    """
    result = ValidationResult(valid=True)

    # Rule: xml_encoding_utf8
    try:
        # Try to encode/decode as UTF-8
        xml_text.encode("utf-8")
    except UnicodeEncodeError as e:
        result.add_error(
            rule_id="xml_encoding_utf8",
            message=f"XML encoding error: {str(e)}. Document must be valid UTF-8",
        )
        return result

    # Rule: xml_wellformed
    try:
        ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError as e:
        result.add_error(
            rule_id="xml_wellformed",
            message=f"XML is not well-formed: {str(e)}",
        )
    except Exception as e:
        result.add_error(
            rule_id="xml_wellformed",
            message=f"Failed to parse XML: {str(e)}",
        )

    return result

