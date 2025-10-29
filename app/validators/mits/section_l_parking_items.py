"""
Section L: Specialized Item — ParkingOfferItem (Rules 75-78)

Validates ParkingOfferItem specific fields and semantics.
"""

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import ParkingElectric, ParkingSpaceType, validate_enum


class SectionLValidator(BaseValidator):
    """
    Validator for Section L: ParkingOfferItem.

    Rules:
        75. Accept optional fields: StructureType, ParkingSpaceSize, SizeType, RegularSpace,
            Handicapped, Electric, SpaceDescription
        76. If ChargeRequirement="Included", enforce Included semantics
        77. Electric uses values: None, Available (strict mode)
        78. RegularSpace and Handicapped use values: Available, None (strict mode)
    """

    section_name = "ParkingOfferItem"
    section_id = "L"

    def validate(self) -> ValidationResult:
        """
        Execute Section L validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            parking_items = class_elem.findall("ParkingOfferItem")

            for item in parking_items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_parking_item(item, item_code, class_code)

        return self.result

    def _validate_parking_item(self, item: ET.Element, item_code: str, class_code: str) -> None:
        """
        Validate a single ParkingOfferItem.

        Args:
            item: ParkingOfferItem element
            item_code: InternalCode of the item
            class_code: Code of the parent class
        """
        item_path = self.get_element_path(item)

        # Rule L.76: Check if ChargeRequirement="Included"
        # If so, amounts must be empty (already validated in Section H)
        characteristics = item.find("Characteristics")
        if characteristics is not None:
            charge_req_elem = characteristics.find("ChargeRequirement")
            if charge_req_elem is not None and self.get_text(charge_req_elem) == "Included":
                # Amounts validation already done in Section H
                pass

        # Rule L.77: Validate Electric field
        electric_elem = item.find("Electric")
        if electric_elem is not None:
            electric = self.get_text(electric_elem)
            if electric:
                valid, error_msg = validate_enum(electric, ParkingElectric, "L.77", "Electric")
                if not valid:
                    self.result.add_error(
                        rule_id="L.77",
                        message=error_msg,
                        element_path=f"{item_path}/Electric",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rule L.78: Validate RegularSpace field
        regular_space_elem = item.find("RegularSpace")
        if regular_space_elem is not None:
            regular_space = self.get_text(regular_space_elem)
            if regular_space:
                valid, error_msg = validate_enum(regular_space, ParkingSpaceType, "L.78", "RegularSpace")
                if not valid:
                    self.result.add_error(
                        rule_id="L.78",
                        message=error_msg,
                        element_path=f"{item_path}/RegularSpace",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rule L.78: Validate Handicapped field
        handicapped_elem = item.find("Handicapped")
        if handicapped_elem is not None:
            handicapped = self.get_text(handicapped_elem)
            if handicapped:
                valid, error_msg = validate_enum(handicapped, ParkingSpaceType, "L.78", "Handicapped")
                if not valid:
                    self.result.add_error(
                        rule_id="L.78",
                        message=error_msg,
                        element_path=f"{item_path}/Handicapped",
                        details={"class_code": class_code, "item_code": item_code},
                    )

