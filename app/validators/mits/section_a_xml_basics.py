"""
Section A: XML Container & Basics (Rules 1-6)

Validates fundamental XML structure and Property identity requirements.
These are critical checks that must pass before proceeding with detailed validation.
"""

import re
from typing import Set

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class SectionAValidator(BaseValidator):
    """
    Validator for Section A: XML Container & Basics.

    Rules:
        1. XML is well-formed (no parse errors) - handled by parser
        2. Encoding is UTF-8 (or declared and decodes successfully) - handled by parser
        3. Single root element is <PhysicalProperty>
        4. <PhysicalProperty> contains ≥1 <Property>
        5. Every <Property> has non-empty @IDValue
        6. @IDValue values are unique across all <Property> elements
    """

    section_name = "XML Container & Basics"
    section_id = "A"

    def validate(self) -> ValidationResult:
        """
        Execute Section A validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Rule A.3: Single root element is <PhysicalProperty>
        if self.root.tag != "PhysicalProperty":
            self.result.add_error(
                rule_id="A.3",
                message=f"Root element must be <PhysicalProperty>, found <{self.root.tag}>",
                element_path=f"/{self.root.tag}",
            )
            return self.result

        # Rule A.4: <PhysicalProperty> contains ≥1 <Property>
        properties = self.root.findall("Property")
        if not properties:
            self.result.add_error(
                rule_id="A.4",
                message="<PhysicalProperty> must contain at least one <Property> element",
                element_path="/PhysicalProperty",
            )
            return self.result

        # Rules A.5 & A.6: Check Property IDValue presence and uniqueness
        property_ids: Set[str] = set()

        for idx, prop in enumerate(properties, start=1):
            id_value = prop.get("IDValue", "").strip()

            # Rule A.5: Every <Property> has non-empty @IDValue
            if not id_value:
                self.result.add_error(
                    rule_id="A.5",
                    message=f"<Property> element #{idx} missing or has empty @IDValue attribute",
                    element_path=f"/PhysicalProperty/Property[{idx}]",
                )
                continue

            # Rule A.6: @IDValue values are unique
            if id_value in property_ids:
                self.result.add_error(
                    rule_id="A.6",
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
    Validate Rules A.1 & A.2: XML well-formedness and encoding.

    This function is called before creating the validator instance since
    it needs to handle parsing errors.

    Args:
        xml_text: Raw XML text to validate

    Returns:
        ValidationResult with any parsing errors
    """
    result = ValidationResult(valid=True)

    # Rule A.2: Encoding is UTF-8 (or declared and decodes successfully)
    try:
        # Try to encode/decode as UTF-8
        xml_text.encode("utf-8")
    except UnicodeEncodeError as e:
        result.add_error(
            rule_id="A.2",
            message=f"XML encoding error: {str(e)}. Document must be valid UTF-8",
        )
        return result

    # Rule A.1: XML is well-formed (no parse errors)
    try:
        ET.fromstring(xml_text.encode("utf-8"))
    except ET.ParseError as e:
        result.add_error(
            rule_id="A.1",
            message=f"XML is not well-formed: {str(e)}",
        )
    except Exception as e:
        result.add_error(
            rule_id="A.1",
            message=f"Failed to parse XML: {str(e)}",
        )

    return result

