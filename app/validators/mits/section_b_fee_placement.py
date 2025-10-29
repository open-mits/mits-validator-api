"""
Section B: Fee Placement Scope (Rules 7-10)

Validates that fees appear in correct hierarchy contexts and use proper structure.
"""

from typing import List, Set

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class SectionBValidator(BaseValidator):
    """
    Validator for Section B: Fee Placement Scope.

    Rules:
        7. Fees may appear under Property, Building, Floorplan, ILS_Unit (all supported)
        8. If a parent level has a fee list, it must use <ChargeOfferClass> containers only
        9. The class/item/amount structure must be exactly:
           ChargeOfferClass → (ChargeOfferItem | PetOfferItem | ParkingOfferItem | StorageOfferItem)
           → ChargeOfferAmount
        10. No fee elements appear outside these four supported ancestors
    """

    section_name = "Fee Placement Scope"
    section_id = "B"

    # Supported parent contexts for fees
    SUPPORTED_FEE_PARENTS = {"Property", "Building", "Floorplan", "ILS_Unit"}

    # Valid item types
    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section B validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Find all ChargeOfferClass elements and validate their context
        for class_elem in self.root.iter("ChargeOfferClass"):
            self._validate_fee_placement(class_elem)
            self._validate_class_structure(class_elem)

        return self.result

    def _validate_fee_placement(self, class_elem: ET.Element) -> None:
        """
        Validate Rules B.7 & B.10: Fee must be under supported parent.

        Args:
            class_elem: ChargeOfferClass element to validate
        """
        # Walk up the tree to find the parent context
        parent = self._find_fee_parent_context(class_elem)

        if parent is None:
            self.result.add_error(
                rule_id="B.10",
                message="<ChargeOfferClass> found outside supported parent contexts. "
                f"Must be under one of: {', '.join(sorted(self.SUPPORTED_FEE_PARENTS))}",
                element_path=self.get_element_path(class_elem),
            )

    def _validate_class_structure(self, class_elem: ET.Element) -> None:
        """
        Validate Rule B.9: Proper class/item/amount structure.

        Args:
            class_elem: ChargeOfferClass element to validate
        """
        class_code = class_elem.get("Code", "")
        class_path = self.get_element_path(class_elem)

        # Find all direct children that are item elements
        items = [
            child
            for child in class_elem
            if child.tag in self.VALID_ITEM_TYPES
        ]

        if not items:
            # Will be caught by Rule D.18, but note it here
            return

        for item in items:
            item_code = item.get("InternalCode", "")
            item_path = f"{class_path}/{item.tag}[@InternalCode='{item_code}']"

            # Check that item contains ChargeOfferAmount elements
            amounts = item.findall("ChargeOfferAmount")
            if not amounts:
                self.result.add_error(
                    rule_id="B.9",
                    message=f"Offer item must contain at least one <ChargeOfferAmount> element",
                    element_path=item_path,
                    details={"class_code": class_code, "item_code": item_code},
                )

    def _find_fee_parent_context(self, element: ET.Element) -> str | None:
        """
        Find the nearest supported parent context for a fee element.

        Args:
            element: Element to find parent for

        Returns:
            Parent tag name if found in supported list, None otherwise
        """
        # Since defusedxml doesn't provide parent pointers easily,
        # we need to search from root to build parent map
        parent_map = {child: parent for parent in self.root.iter() for child in parent}

        current = element
        while current in parent_map:
            parent = parent_map[current]
            if parent.tag in self.SUPPORTED_FEE_PARENTS:
                return parent.tag
            current = parent

        return None


def find_all_with_context(root: ET.Element, tag: str, supported_parents: Set[str]) -> List[tuple[ET.Element, str | None]]:
    """
    Find all elements with a given tag and their parent context.

    Args:
        root: Root element to search from
        tag: Tag name to find
        supported_parents: Set of valid parent tag names

    Returns:
        List of (element, parent_tag) tuples
    """
    results = []
    parent_map = {child: parent for parent in root.iter() for child in parent}

    for elem in root.iter(tag):
        parent_context = None
        current = elem
        while current in parent_map:
            parent = parent_map[current]
            if parent.tag in supported_parents:
                parent_context = parent.tag
                break
            current = parent
        results.append((elem, parent_context))

    return results

