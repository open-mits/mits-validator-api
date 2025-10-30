"""
Section D: ChargeOfferClass — Existence & Code Rules (Rules 15-20)

Validates the structure and identity of ChargeOfferClass elements.
"""

from typing import Dict, List, Set

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class ChargeClassValidator(BaseValidator):
    """
    Validator for Section D: ChargeOfferClass Structure.

    Rules:
        15. Each <ChargeOfferClass> has required non-empty Code attribute
        16. Allowed to repeat the same Code across different ancestors
        17. Within the same parent, class Code values are unique
        18. Each class contains ≥1 offer item (standard or specialized)
        19. No empty/whitespace-only text nodes inside <ChargeOfferClass> children
        20. Optional <Limits> element is allowed; if absent, skip limit checks
    """

    section_name = "ChargeOfferClass Structure"
    section_id = "charge_class"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    VALID_CLASS_CHILDREN = VALID_ITEM_TYPES | {
        "Limits",
        "Description",  # Sometimes present
        "Name",  # Sometimes present
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section D validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Build a map of classes grouped by their immediate parent
        classes_by_parent: Dict[str, List[Element]] = {}

        for class_elem in self.root.iter("ChargeOfferClass"):
            # Rule D.15: Check for Code attribute
            code = class_elem.get("Code", "").strip()
            class_path = self.get_element_path(class_elem)

            if not code:
                # Try to get identifying information for better error message
                identifiers = []
                
                # Try Name first
                name_elem = class_elem.find("Name")
                name = self.get_text(name_elem) if name_elem is not None else None
                if name:
                    identifiers.append(f"Name='{name}'")
                
                # Try Description
                desc_elem = class_elem.find("Description")
                desc = self.get_text(desc_elem) if desc_elem is not None else None
                if desc and not name:  # Only use if no name
                    identifiers.append(f"Description='{desc[:50]}...'")  # Truncate long descriptions
                
                # Try to find first child item for additional context
                if not identifiers:
                    for child in class_elem:
                        if child.tag in self.VALID_ITEM_TYPES:
                            child_code = child.get("InternalCode", "").strip()
                            if child_code:
                                identifiers.append(f"containing item '{child_code}'")
                                break
                            child_name_elem = child.find("Name")
                            child_name = self.get_text(child_name_elem) if child_name_elem is not None else None
                            if child_name:
                                identifiers.append(f"containing '{child_name}'")
                                break
                
                # Build the message
                if identifiers:
                    message = f"<ChargeOfferClass> with {identifiers[0]} missing required non-empty 'Code' attribute"
                    details = {"identifier": identifiers[0]}
                else:
                    message = f"<ChargeOfferClass> at {class_path} missing required non-empty 'Code' attribute"
                    details = {}
                
                self.result.add_error(
                    rule_id="class_has_code",
                    message=message,
                    element_path=class_path,
                    details=details,
                )
                continue

            # Rule D.18: Check for at least one offer item
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]
            if not items:
                self.result.add_error(
                    rule_id="class_has_items",
                    message=f"<ChargeOfferClass Code='{code}'> must contain at least one offer item "
                    f"({', '.join(sorted(self.VALID_ITEM_TYPES))})",
                    element_path=class_path,
                    details={"code": code},
                )

            # Rule D.19: Check for empty/whitespace-only text nodes
            for child in class_elem:
                if child.tag not in self.VALID_CLASS_CHILDREN:
                    # Unknown child element
                    self.result.add_warning(
                        rule_id="class_no_empty_children",
                        message=f"<ChargeOfferClass Code='{code}'> contains unexpected child element <{child.tag}>",
                        element_path=f"{class_path}/{child.tag}",
                        details={"code": code, "unexpected_element": child.tag},
                    )

                # Check for text content that is empty or whitespace only
                if child.text and not child.text.strip():
                    # Only report if it's truly empty (not just trimmed)
                    if child.text:
                        self.result.add_warning(
                            rule_id="class_no_empty_children",
                            message=f"<ChargeOfferClass Code='{code}'>/<{child.tag}> "
                            f"contains whitespace-only text content",
                            element_path=f"{class_path}/{child.tag}",
                            details={"code": code},
                        )

            # Group by parent for uniqueness check (Rule D.17)
            parent_key = self._get_parent_key(class_elem)
            if parent_key not in classes_by_parent:
                classes_by_parent[parent_key] = []
            classes_by_parent[parent_key].append(class_elem)

        # Rule D.17: Check code uniqueness within each parent
        for parent_key, classes in classes_by_parent.items():
            self._check_code_uniqueness(classes, parent_key)

        return self.result

    def _get_parent_key(self, element: Element) -> str:
        """
        Get a unique key identifying the parent of an element.

        Args:
            element: Element to get parent key for

        Returns:
            String key representing parent context
        """
        # Build parent map
        parent_map = {child: parent for parent in self.root.iter() for child in parent}

        if element not in parent_map:
            return "root"

        parent = parent_map[element]
        parent_id = parent.get("IDValue") or parent.get("InternalCode") or parent.get("Code")

        if parent_id:
            return f"{parent.tag}[@id='{parent_id}']"
        return f"{parent.tag}"

    def _check_code_uniqueness(self, classes: List[Element], parent_key: str) -> None:
        """
        Check that Code values are unique within a parent context.

        Args:
            classes: List of ChargeOfferClass elements under the same parent
            parent_key: Parent identifier for error messages
        """
        seen_codes: Set[str] = set()

        for class_elem in classes:
            code = class_elem.get("Code", "").strip()
            if not code:
                continue  # Already reported in Rule D.15

            if code in seen_codes:
                self.result.add_error(
                    rule_id="class_code_unique_in_parent",
                    message=f"Duplicate <ChargeOfferClass Code='{code}'> found within parent {parent_key}. "
                    f"Class Codes must be unique within the same parent",
                    element_path=self.get_element_path(class_elem),
                    details={"code": code, "parent": parent_key},
                )
            else:
                seen_codes.add(code)

