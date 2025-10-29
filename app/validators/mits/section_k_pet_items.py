"""
Section K: Specialized Item — PetOfferItem (Rules 70-74)

Validates PetOfferItem specific fields and semantics.
"""

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import PetAllowed, validate_enum


class SectionKValidator(BaseValidator):
    """
    Validator for Section K: PetOfferItem.

    Rules:
        70. Accept optional fields: Allowed, PetBreedorType, MaximumSize, MaximumWeight, PetCare
        71. If Allowed present, value is "Yes" or "No"
        72. If Allowed="No", all amount blocks must be empty
        73. MaximumWeight if present must be a number with optional unit suffix
        74. Pet deposit vs pet fee: if Refundability=Deposit, RefundabilityMaxType/Max required
    """

    section_name = "PetOfferItem"
    section_id = "K"

    def validate(self) -> ValidationResult:
        """
        Execute Section K validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            pet_items = class_elem.findall("PetOfferItem")

            for item in pet_items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_pet_item(item, item_code, class_code)

        return self.result

    def _validate_pet_item(self, item: ET.Element, item_code: str, class_code: str) -> None:
        """
        Validate a single PetOfferItem.

        Args:
            item: PetOfferItem element
            item_code: InternalCode of the item
            class_code: Code of the parent class
        """
        item_path = self.get_element_path(item)

        # Rule K.71: Validate Allowed field
        allowed_elem = item.find("Allowed")
        if allowed_elem is not None:
            allowed = self.get_text(allowed_elem)
            if allowed:
                valid, error_msg = validate_enum(allowed, PetAllowed, "K.71", "Allowed")
                if not valid:
                    self.result.add_error(
                        rule_id="K.71",
                        message=error_msg,
                        element_path=f"{item_path}/Allowed",
                        details={"class_code": class_code, "item_code": item_code},
                    )

                # Rule K.72: If Allowed="No", all amounts must be empty
                if allowed == "No":
                    amount_blocks = item.findall("ChargeOfferAmount")
                    for idx, block in enumerate(amount_blocks, start=1):
                        amounts_elem = block.find("Amounts")
                        percentage_elem = block.find("Percentage")

                        amounts_text = self.get_text(amounts_elem) if amounts_elem is not None else ""
                        percentage_text = self.get_text(percentage_elem) if percentage_elem is not None else ""

                        if amounts_text:
                            self.result.add_error(
                                rule_id="K.72",
                                message=f"Pet item '{item_code}' has Allowed='No' but non-empty <Amounts>='{amounts_text}'. "
                                f"Amounts must be empty when pets are not allowed",
                                element_path=f"{item_path}/ChargeOfferAmount[{idx}]/Amounts",
                                details={"class_code": class_code, "item_code": item_code},
                            )

                        if percentage_text:
                            self.result.add_error(
                                rule_id="K.72",
                                message=f"Pet item '{item_code}' has Allowed='No' but non-empty <Percentage>='{percentage_text}'. "
                                f"Percentage must be empty when pets are not allowed",
                                element_path=f"{item_path}/ChargeOfferAmount[{idx}]/Percentage",
                                details={"class_code": class_code, "item_code": item_code},
                            )

        # Rule K.73: Validate MaximumWeight format
        max_weight_elem = item.find("MaximumWeight")
        if max_weight_elem is not None:
            max_weight = self.get_text(max_weight_elem)
            if max_weight:
                # Must contain a number, optional unit suffix (e.g., "50lb", "25kg", "30")
                import re

                # Pattern: number (optional decimal) followed by optional unit
                pattern = r"^\d+(\.\d+)?\s*(lb|lbs|kg|kgs|pounds|kilos)?$"
                if not re.match(pattern, max_weight, re.IGNORECASE):
                    self.result.add_error(
                        rule_id="K.73",
                        message=f"Pet item '{item_code}' has invalid <MaximumWeight>='{max_weight}'. "
                        f"Expected format: number with optional unit (e.g., '50lb', '25kg', '30')",
                        element_path=f"{item_path}/MaximumWeight",
                        details={"class_code": class_code, "item_code": item_code, "value": max_weight},
                    )

        # Rule K.74: Pet deposit requires RefundabilityMaxType/Max
        # This is already validated in Section G, just add specific note for pets
        characteristics = item.find("Characteristics")
        if characteristics is not None:
            refund_elem = characteristics.find("Refundability")
            if refund_elem is not None:
                refund = self.get_text(refund_elem)
                if refund == "Deposit":
                    max_type_elem = characteristics.find("RefundabilityMaxType")
                    max_elem = characteristics.find("RefundabilityMax")

                    if not (max_type_elem is not None and self.get_text(max_type_elem)):
                        self.result.add_error(
                            rule_id="K.74",
                            message=f"Pet deposit '{item_code}' has Refundability='Deposit' but missing <RefundabilityMaxType>",
                            element_path=f"{item_path}/Characteristics",
                            details={"class_code": class_code, "item_code": item_code},
                        )

                    if not (max_elem is not None and self.get_text(max_elem)):
                        self.result.add_error(
                            rule_id="K.74",
                            message=f"Pet deposit '{item_code}' has Refundability='Deposit' but missing <RefundabilityMax>",
                            element_path=f"{item_path}/Characteristics",
                            details={"class_code": class_code, "item_code": item_code},
                        )

