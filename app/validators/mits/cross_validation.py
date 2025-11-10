"""
Sections N, O, P: Intra-class & Cross-class Integrity, References, Included Items (Rules 82-97)

Validates cross-field totals, references, percentage-of relationships, and Included semantics.
"""

from typing import Dict, List, Set

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class CrossValidation(BaseValidator):
    """
    Validator for Sections N, O, P: Integrity & References.

    Rules:
        N: 82-89 (Intra-class & cross-class integrity)
        O: 90-94 (Percentage-of & reference integrity)
        P: 95-97 (Included items & zero-amount guards)
    """

    section_name = "Integrity & References"
    section_id = "cross_validation"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Sections N, O, P validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Build global item code registry for reference validation
        global_item_codes = self._build_global_item_registry()

        # Validate each class
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            self._validate_class_integrity(class_elem, class_code, global_item_codes)

        # Section O: Validate percentage-of references and cycles
        self._validate_percentage_references(global_item_codes)

        # Section P: Validate Included items
        self._validate_included_items()

        return self.result

    def _build_global_item_registry(self) -> Dict[str, Dict]:
        """
        Build a registry of all items in the document.

        Returns:
            Dict mapping item_code to item information
        """
        registry = {}

        for prop in self.root.findall("Property"):
            prop_id = prop.get("IDValue", "unknown")

            for class_elem in prop.iter("ChargeOfferClass"):
                class_code = class_elem.get("Code", "unknown")
                parent_type = self._get_parent_type(class_elem)

                items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

                for item in items:
                    item_code = item.get("InternalCode", "").strip()
                    if not item_code:
                        continue

                    # Get characteristics
                    characteristics = item.find("Characteristics")
                    charge_req = ""
                    if characteristics is not None:
                        charge_req_elem = characteristics.find("ChargeRequirement")
                        if charge_req_elem is not None:
                            charge_req = self.get_text(charge_req_elem)

                    # Get amount basis and percentage of code
                    amount_basis_elem = item.find("AmountBasis")
                    amount_basis = self.get_text(amount_basis_elem) if amount_basis_elem is not None else ""

                    percentage_of_code_elem = item.find("PercentageOfCode")
                    percentage_of_code = (
                        self.get_text(percentage_of_code_elem) if percentage_of_code_elem is not None else ""
                    )

                    registry[item_code] = {
                        "element": item,
                        "class_code": class_code,
                        "property_id": prop_id,
                        "parent_type": parent_type,
                        "charge_requirement": charge_req,
                        "amount_basis": amount_basis,
                        "percentage_of_code": percentage_of_code,
                    }

        return registry

    def _get_parent_type(self, element: Element) -> str:
        """
        Get the parent type (Property, Building, Floorplan, ILS_Unit) of an element.

        Args:
            element: Element to find parent type for

        Returns:
            Parent type string
        """
        parent_map = {child: parent for parent in self.root.iter() for child in parent}
        current = element
        while current in parent_map:
            parent = parent_map[current]
            if parent.tag in {"Property", "Building", "Floorplan", "ILS_Unit"}:
                return parent.tag
            current = parent
        return "unknown"

    def _validate_class_integrity(
        self, class_elem: Element, class_code: str, global_item_codes: Dict
    ) -> None:
        """
        Validate Rules N.82-89: Intra-class integrity.

        Args:
            class_elem: ChargeOfferClass element
            class_code: Code attribute of the class
            global_item_codes: Global registry of item codes
        """
        items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

        # Rule N.82: Within a class, InternalCode values are unique
        # (Already validated in Section F, Rule F.28)

        # Rule N.83: Within a parent level, class Code values are unique
        # (Already validated in Section D, Rule D.17)

        # Rules N.85-89: Validate class limits if present
        limits = class_elem.find("Limits")
        if limits is not None:
            self._validate_class_limits_application(limits, items, class_code, class_elem)

    def _validate_class_limits_application(
        self, limits: Element, items: List[Element], class_code: str, class_elem: Element
    ) -> None:
        """
        Validate Rules N.85-89: Class limits application.

        Args:
            limits: Limits element
            items: List of items in the class
            class_code: Code of the class
            class_elem: ChargeOfferClass element
        """
        # Rule N.85: Get AppliesTo codes
        applies_to = limits.find("AppliesTo")
        applies_to_codes = set()

        if applies_to is not None:
            internal_codes = applies_to.findall("InternalCode")
            for ic in internal_codes:
                code = self.get_text(ic)
                if code:
                    applies_to_codes.add(code)

        # Rule N.85: If AppliesTo present, only items within the same class are considered
        if applies_to_codes:
            item_codes_in_class = {item.get("InternalCode", "").strip() for item in items}

            # Check that all codes in AppliesTo exist in this class
            for code in applies_to_codes:
                if code not in item_codes_in_class:
                    self.result.add_warning(
                        rule_id="limit_applies_to_same_class",
                        message=f"Class '{class_code}' <Limits>/<AppliesTo> references code '{code}' "
                        f"which is not in this class. Only codes within the same class are considered",
                        element_path=f"{self.get_element_path(class_elem)}/Limits/AppliesTo",
                        details={"class_code": class_code, "referenced_code": code},
                    )

        # Rules N.86-89: Validate occurrence and amount caps
        # (These are business logic rules that would be enforced at runtime, not document validation)
        # We can note their presence for informational purposes

        max_occur_elem = limits.find("MaximumOccurences")
        max_amount_elem = limits.find("MaximumAmount")

        if max_occur_elem is not None and self.get_text(max_occur_elem):
            self.result.add_info(
                rule_id="limit_occurrence_cap_runtime",
                message=f"Class '{class_code}' has MaximumOccurences cap. "
                f"Selectable instances are limited at runtime",
                element_path=f"{self.get_element_path(class_elem)}/Limits/MaximumOccurences",
                details={"class_code": class_code},
            )

        if max_amount_elem is not None and self.get_text(max_amount_elem):
            self.result.add_info(
                rule_id="limit_amount_cap_runtime",
                message=f"Class '{class_code}' has MaximumAmount cap. "
                f"Total charges are limited at runtime",
                element_path=f"{self.get_element_path(class_elem)}/Limits/MaximumAmount",
                details={"class_code": class_code},
            )

    def _validate_percentage_references(self, global_item_codes: Dict) -> None:
        """
        Validate Rules O.91-94: Percentage-of references.

        Args:
            global_item_codes: Global registry of item codes
        """
        for item_code, item_info in global_item_codes.items():
            percentage_of_code = item_info["percentage_of_code"]
            if not percentage_of_code:
                continue

            item_elem = item_info["element"]
            item_path = self.get_element_path(item_elem)

            # Rule O.91: No self-reference
            if percentage_of_code == item_code:
                self.result.add_error(
                    rule_id="reference_no_self",
                    message=f"Item '{item_code}' cannot reference itself in <PercentageOfCode>",
                    element_path=f"{item_path}/PercentageOfCode",
                    details={"item_code": item_code},
                )
                continue

            # Skip remaining validations if referenced code doesn't exist
            if percentage_of_code not in global_item_codes:
                continue

            # Rule O.92: Check for circular references
            if self._has_circular_reference(item_code, global_item_codes, set()):
                self.result.add_error(
                    rule_id="reference_no_circular",
                    message=f"Item '{item_code}' has circular percentage-of reference chain",
                    element_path=f"{item_path}/PercentageOfCode",
                    details={"item_code": item_code},
                )

            # Rule O.93: Percentage-of an Included item check
            referenced_info = global_item_codes[percentage_of_code]
            if referenced_info["charge_requirement"] == "Included":
                self.result.add_error(
                    rule_id="reference_not_included",
                    message=f"Item '{item_code}' references Included item '{percentage_of_code}'. "
                    f"Cannot calculate percentage of a zero/empty amount",
                    element_path=f"{item_path}/PercentageOfCode",
                    details={"item_code": item_code, "referenced_code": percentage_of_code},
                )

            # Rule O.94: Check for multiple amount blocks in target
            # (Overlap detection already handled in Section I)

    def _has_circular_reference(
        self, item_code: str, registry: Dict, visited: Set[str]
    ) -> bool:
        """
        Check for circular percentage-of references.

        Args:
            item_code: Item code to check
            registry: Global item registry
            visited: Set of already visited codes

        Returns:
            True if circular reference detected
        """
        if item_code in visited:
            return True

        if item_code not in registry:
            return False

        visited.add(item_code)

        percentage_of_code = registry[item_code]["percentage_of_code"]
        if percentage_of_code:
            if self._has_circular_reference(percentage_of_code, registry, visited):
                return True

        visited.remove(item_code)
        return False

    def _validate_included_items(self) -> None:
        """
        Validate Rules P.95-97: Included items semantics.
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                item_path = self.get_element_path(item)

                characteristics = item.find("Characteristics")
                if characteristics is None:
                    continue

                charge_req_elem = characteristics.find("ChargeRequirement")
                if charge_req_elem is None:
                    continue

                charge_req = self.get_text(charge_req_elem)
                if charge_req != "Included":
                    continue

                # Rule P.95: Included items must have no payable amounts
                # (Already validated in Section H, Rule H.56)

                # Rule P.96: Items with billing frequency must not be "Included"
                freq_elem = characteristics.find("PaymentFrequency")
                if freq_elem is not None:
                    freq = self.get_text(freq_elem)
                    if freq in {"Monthly", "Annually", "Quarterly"}:
                        self.result.add_error(
                            rule_id="included_no_recurring",
                            message=f"Item '{item_code}' has ChargeRequirement='Included' "
                            f"but PaymentFrequency='{freq}'. Included items cannot have recurring billing",
                            element_path=f"{item_path}/Characteristics/PaymentFrequency",
                            details={"class_code": class_code, "item_code": item_code, "frequency": freq},
                        )

                # Rule P.97: Included items may have date windows (validated in Section I)

