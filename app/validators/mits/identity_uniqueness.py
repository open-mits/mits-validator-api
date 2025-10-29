"""
Section C: Per-Level Identity Hygiene (Rules 11-14)

Validates identity uniqueness and quality across Property hierarchy levels.
"""

from typing import Dict, Set

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class IdentityUniquenessValidator(BaseValidator):
    """
    Validator for Section C: Per-Level Identity Hygiene.

    Rules:
        11. Each <Building> under a Property has unique @IDValue (within that Property)
        12. Each <Floorplan> under a Property has unique @IDValue (within that Property)
        13. Each <ILS_Unit> under a Property has unique @IDValue (within that Property)
        14. Identity values (IDs) are non-empty strings without leading/trailing whitespace
    """

    section_name = "Per-Level Identity Hygiene"
    section_id = "identity_uniqueness"

    def validate(self) -> ValidationResult:
        """
        Execute Section C validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Process each Property separately
        for prop in self.root.findall("Property"):
            prop_id = prop.get("IDValue", "unknown")
            self._validate_property_identities(prop, prop_id)

        return self.result

    def _validate_property_identities(self, property_elem: Element, property_id: str) -> None:
        """
        Validate identity uniqueness within a single Property.

        Args:
            property_elem: Property element to validate
            property_id: ID of the property for error messages
        """
        # Rule 11: Validate Building IDs
        self._validate_element_ids(
            property_elem,
            "Building",
            property_id,
            "building_id_unique",
        )

        # Rule 12: Validate Floorplan IDs
        self._validate_element_ids(
            property_elem,
            "Floorplan",
            property_id,
            "floorplan_id_unique",
        )

        # Rule 13: Validate ILS_Unit IDs
        self._validate_element_ids(
            property_elem,
            "ILS_Unit",
            property_id,
            "unit_id_unique",
        )

    def _validate_element_ids(
        self,
        parent: Element,
        element_tag: str,
        property_id: str,
        rule_id: str,
    ) -> None:
        """
        Validate ID uniqueness for a specific element type within a parent.

        Args:
            parent: Parent element to search within
            element_tag: Tag name of elements to validate
            property_id: Property ID for error messages
            rule_id: Rule identifier for errors
        """
        seen_ids: Set[str] = set()
        elements = parent.findall(f".//{element_tag}")

        for idx, elem in enumerate(elements, start=1):
            id_value = elem.get("IDValue", "")

            # Rule 14: IDs must be non-empty without leading/trailing whitespace
            if not id_value:
                self.result.add_error(
                    rule_id="id_no_whitespace",
                    message=f"<{element_tag}> element #{idx} in Property '{property_id}' "
                    f"has empty @IDValue attribute",
                    element_path=f"/Property[@IDValue='{property_id}']//{element_tag}[{idx}]",
                )
                continue

            if id_value != id_value.strip():
                self.result.add_error(
                    rule_id="id_no_whitespace",
                    message=f"<{element_tag}> @IDValue '{id_value}' in Property '{property_id}' "
                    f"has leading or trailing whitespace",
                    element_path=f"/Property[@IDValue='{property_id}']//{element_tag}[@IDValue='{id_value}']",
                    details={"id_value": id_value, "trimmed": id_value.strip()},
                )
                # Use trimmed version for uniqueness check
                id_value = id_value.strip()

            # Check uniqueness within this Property
            if id_value in seen_ids:
                self.result.add_error(
                    rule_id=rule_id,
                    message=f"Duplicate <{element_tag}> @IDValue '{id_value}' found in Property '{property_id}'. "
                    f"IDs must be unique within each Property",
                    element_path=f"/Property[@IDValue='{property_id}']//{element_tag}[@IDValue='{id_value}']",
                    details={"duplicate_id": id_value, "property_id": property_id},
                )
            else:
                seen_ids.add(id_value)

