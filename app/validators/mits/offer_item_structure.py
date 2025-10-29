"""
Section F: Offer Item — Common Structure (Rules 27-41)

Validates the common structure of all offer items (ChargeOfferItem and specialized items).
"""

from decimal import Decimal, InvalidOperation

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class OfferItemStructureValidator(BaseValidator):
    """
    Validator for Section F: Offer Item Common Structure.

    Rules:
        27. Each item has required non-empty InternalCode (attribute)
        28. InternalCode values are unique within the parent class
        29. Items with identical semantics must not be duplicated
        30. Required <Name> element present and non-empty
        31. Required <Description> element present and non-empty
        32. Exactly one <Characteristics> block per item
        33. Item contains ≥1 <ChargeOfferAmount> child
        34. Optional <ItemMinimumOccurrences> is integer ≥ 0, if present
        35. Optional <ItemMaximumOccurrences> is integer ≥ 1, if present
        36. If both item min/max present: min ≤ max
        37. Optional <AmountBasis> can be empty only if ChargeRequirement="Included"
        38. Optional <PercentageOfCode> present only when AmountBasis="Percentage Of"
        39. Optional <AmountPerType> if present uses valid enumeration
        40. Optional PMS passthrough fields may appear
        41. No unexpected/unknown child elements
    """

    section_name = "Offer Item Structure"
    section_id = "offer_item_structure"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    COMMON_ITEM_CHILDREN = {
        "Name",
        "Description",
        "Characteristics",
        "ItemMinimumOccurrences",
        "ItemMaximumOccurrences",
        "AmountBasis",
        "PercentageOfCode",
        "AmountPerType",
        "ChargeOfferAmount",
        # PMS passthrough fields
        "PmsItemCode",
        "PmsItemDescription",
        "PmsItemCategory",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section F validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            self._validate_class_items(class_elem, class_code)

        return self.result

    def _validate_class_items(self, class_elem: Element, class_code: str) -> None:
        """
        Validate all items within a ChargeOfferClass.

        Args:
            class_elem: ChargeOfferClass element
            class_code: Code attribute of the class
        """
        items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]
        internal_codes = set()

        for item in items:
            item_code = item.get("InternalCode", "").strip()
            item_path = f"{self.get_element_path(class_elem)}/{item.tag}"

            # Rule F.27: InternalCode is required and non-empty
            if not item_code:
                self.result.add_error(
                    rule_id="item_has_internal_code",
                    message=f"Offer item in class '{class_code}' missing required non-empty 'InternalCode' attribute",
                    element_path=item_path,
                    details={"class_code": class_code},
                )
                continue

            item_path = f"{item_path}[@InternalCode='{item_code}']"

            # Rule F.28: InternalCode values are unique within parent class
            if item_code in internal_codes:
                self.result.add_error(
                    rule_id="item_internal_code_unique",
                    message=f"Duplicate InternalCode '{item_code}' found in class '{class_code}'. "
                    f"Codes must be unique within the same ChargeOfferClass",
                    element_path=item_path,
                    details={"class_code": class_code, "internal_code": item_code},
                )
            else:
                internal_codes.add(item_code)

            # Validate required and optional fields
            self._validate_item_structure(item, item_code, class_code, item_path)

    def _validate_item_structure(
        self, item: Element, item_code: str, class_code: str, item_path: str
    ) -> None:
        """
        Validate the structure of a single offer item.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        # Rule F.30: Required <Name> element
        name_elem = item.find("Name")
        if name_elem is None:
            self.result.add_error(
                rule_id="item_has_name",
                message=f"Item '{item_code}' in class '{class_code}' missing required <Name> element",
                element_path=item_path,
                details={"class_code": class_code, "item_code": item_code},
            )
        elif not self.get_text(name_elem):
            self.result.add_error(
                rule_id="item_has_name",
                message=f"Item '{item_code}' in class '{class_code}' has empty <Name> element",
                element_path=f"{item_path}/Name",
                details={"class_code": class_code, "item_code": item_code},
            )

        # Rule F.31: Required <Description> element
        desc_elem = item.find("Description")
        if desc_elem is None:
            self.result.add_error(
                rule_id="item_has_description",
                message=f"Item '{item_code}' in class '{class_code}' missing required <Description> element",
                element_path=item_path,
                details={"class_code": class_code, "item_code": item_code},
            )
        elif not self.get_text(desc_elem):
            self.result.add_error(
                rule_id="item_has_description",
                message=f"Item '{item_code}' in class '{class_code}' has empty <Description> element",
                element_path=f"{item_path}/Description",
                details={"class_code": class_code, "item_code": item_code},
            )

        # Rule F.32: Exactly one <Characteristics> block
        characteristics = item.findall("Characteristics")
        if len(characteristics) == 0:
            self.result.add_error(
                rule_id="item_has_one_characteristics",
                message=f"Item '{item_code}' in class '{class_code}' missing required <Characteristics> element",
                element_path=item_path,
                details={"class_code": class_code, "item_code": item_code},
            )
        elif len(characteristics) > 1:
            self.result.add_error(
                rule_id="item_has_one_characteristics",
                message=f"Item '{item_code}' in class '{class_code}' has multiple <Characteristics> elements. "
                f"Only one is allowed",
                element_path=item_path,
                details={"class_code": class_code, "item_code": item_code, "count": len(characteristics)},
            )

        # Rule F.33: Item contains ≥1 ChargeOfferAmount
        amounts = item.findall("ChargeOfferAmount")
        if not amounts:
            self.result.add_error(
                rule_id="item_has_amount_blocks",
                message=f"Item '{item_code}' in class '{class_code}' must contain at least one "
                f"<ChargeOfferAmount> element",
                element_path=item_path,
                details={"class_code": class_code, "item_code": item_code},
            )

        # Rules F.34, F.35, F.36: Validate occurrence constraints
        self._validate_occurrences(item, item_code, class_code, item_path)

        # Rule F.41: Check for unexpected children
        self._check_unexpected_children(item, item_code, class_code, item_path)

    def _validate_occurrences(
        self, item: Element, item_code: str, class_code: str, item_path: str
    ) -> None:
        """
        Validate ItemMinimumOccurrences and ItemMaximumOccurrences.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        min_occur_elem = item.find("ItemMinimumOccurrences")
        max_occur_elem = item.find("ItemMaximumOccurrences")

        min_occur = None
        max_occur = None

        # Rule F.34: ItemMinimumOccurrences is integer ≥ 0
        if min_occur_elem is not None:
            min_text = self.get_text(min_occur_elem)
            if min_text:
                try:
                    min_occur = int(min_text)
                    if min_occur < 0:
                        self.result.add_error(
                            rule_id="item_min_occurrence_valid",
                            message=f"<ItemMinimumOccurrences> in item '{item_code}' must be ≥ 0, found '{min_text}'",
                            element_path=f"{item_path}/ItemMinimumOccurrences",
                            details={"class_code": class_code, "item_code": item_code},
                        )
                except ValueError:
                    self.result.add_error(
                        rule_id="item_min_occurrence_valid",
                        message=f"<ItemMinimumOccurrences> in item '{item_code}' must be an integer, found '{min_text}'",
                        element_path=f"{item_path}/ItemMinimumOccurrences",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rule F.35: ItemMaximumOccurrences is integer ≥ 1
        if max_occur_elem is not None:
            max_text = self.get_text(max_occur_elem)
            if max_text:
                try:
                    max_occur = int(max_text)
                    if max_occur < 1:
                        self.result.add_error(
                            rule_id="item_max_occurrence_valid",
                            message=f"<ItemMaximumOccurrences> in item '{item_code}' must be ≥ 1, found '{max_text}'",
                            element_path=f"{item_path}/ItemMaximumOccurrences",
                            details={"class_code": class_code, "item_code": item_code},
                        )
                except ValueError:
                    self.result.add_error(
                        rule_id="item_max_occurrence_valid",
                        message=f"<ItemMaximumOccurrences> in item '{item_code}' must be an integer, found '{max_text}'",
                        element_path=f"{item_path}/ItemMaximumOccurrences",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rule F.36: If both present, min ≤ max
        if min_occur is not None and max_occur is not None:
            if min_occur > max_occur:
                self.result.add_error(
                    rule_id="item_occurrence_range_valid",
                    message=f"Item '{item_code}' has ItemMinimumOccurrences ({min_occur}) > "
                    f"ItemMaximumOccurrences ({max_occur}). Min must be ≤ Max",
                    element_path=item_path,
                    details={"class_code": class_code, "item_code": item_code, "min": min_occur, "max": max_occur},
                )

    def _check_unexpected_children(
        self, item: Element, item_code: str, class_code: str, item_path: str
    ) -> None:
        """
        Check for unexpected child elements in an item.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        # Get specialized children based on item type
        specialized_children = set()
        if item.tag == "PetOfferItem":
            specialized_children = {
                "Allowed",
                "PetBreedorType",
                "MaximumSize",
                "MaximumWeight",
                "PetCare",
            }
        elif item.tag == "ParkingOfferItem":
            specialized_children = {
                "StructureType",
                "ParkingSpaceSize",
                "SizeType",
                "RegularSpace",
                "Handicapped",
                "Electric",
                "SpaceDescription",
            }
        elif item.tag == "StorageOfferItem":
            specialized_children = {
                "StorageType",
                "StorageUoM",
                "Height",
                "Width",
                "Length",
            }

        allowed_children = self.COMMON_ITEM_CHILDREN | specialized_children

        for child in item:
            if child.tag not in allowed_children:
                self.result.add_warning(
                    rule_id="item_no_unexpected_children",
                    message=f"Item '{item_code}' contains unexpected child element <{child.tag}>",
                    element_path=f"{item_path}/{child.tag}",
                    details={"class_code": class_code, "item_code": item_code},
                )

