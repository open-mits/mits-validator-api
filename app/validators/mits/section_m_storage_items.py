"""
Section M: Specialized Item — StorageOfferItem (Rules 79-81)

Validates StorageOfferItem specific fields and semantics.
"""

from decimal import Decimal, InvalidOperation

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class SectionMValidator(BaseValidator):
    """
    Validator for Section M: StorageOfferItem.

    Rules:
        79. Accept optional fields: StorageType, StorageUoM, Height, Width, Length
        80. Dimensions (if present) are decimals ≥ 0
        81. StorageUoM (if present) must match recognized unit token
    """

    section_name = "StorageOfferItem"
    section_id = "M"

    # Common unit of measure tokens for storage
    VALID_STORAGE_UNITS = {
        "sqft",
        "sq ft",
        "square feet",
        "sqm",
        "sq m",
        "square meters",
        "cuft",
        "cu ft",
        "cubic feet",
        "cum",
        "cu m",
        "cubic meters",
        "ft",
        "feet",
        "m",
        "meters",
        "in",
        "inches",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section M validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            storage_items = class_elem.findall("StorageOfferItem")

            for item in storage_items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_storage_item(item, item_code, class_code)

        return self.result

    def _validate_storage_item(self, item: ET.Element, item_code: str, class_code: str) -> None:
        """
        Validate a single StorageOfferItem.

        Args:
            item: StorageOfferItem element
            item_code: InternalCode of the item
            class_code: Code of the parent class
        """
        item_path = self.get_element_path(item)

        # Rule M.80: Validate dimension fields (Height, Width, Length)
        for dimension_field in ["Height", "Width", "Length"]:
            dim_elem = item.find(dimension_field)
            if dim_elem is not None:
                dim_value = self.get_text(dim_elem)
                if dim_value:
                    try:
                        dim_decimal = Decimal(dim_value)
                        if dim_decimal < 0:
                            self.result.add_error(
                                rule_id="M.80",
                                message=f"Storage item '{item_code}' <{dimension_field}> must be ≥ 0, found '{dim_value}'",
                                element_path=f"{item_path}/{dimension_field}",
                                details={"class_code": class_code, "item_code": item_code, "value": dim_value},
                            )
                    except (InvalidOperation, ValueError):
                        self.result.add_error(
                            rule_id="M.80",
                            message=f"Storage item '{item_code}' <{dimension_field}> must be a valid decimal, found '{dim_value}'",
                            element_path=f"{item_path}/{dimension_field}",
                            details={"class_code": class_code, "item_code": item_code, "value": dim_value},
                        )

        # Rule M.81: Validate StorageUoM
        uom_elem = item.find("StorageUoM")
        if uom_elem is not None:
            uom = self.get_text(uom_elem).lower()
            if uom and uom not in self.VALID_STORAGE_UNITS:
                self.result.add_error(
                    rule_id="M.81",
                    message=f"Storage item '{item_code}' has unrecognized <StorageUoM>='{uom}'. "
                    f"Expected one of: {', '.join(sorted(self.VALID_STORAGE_UNITS))}",
                    element_path=f"{item_path}/StorageUoM",
                    details={"class_code": class_code, "item_code": item_code, "value": uom},
                )

