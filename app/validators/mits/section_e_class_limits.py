"""
Section E: Class Limits (Rules 21-26)

Validates the Limits element within ChargeOfferClass.
"""

from decimal import Decimal, InvalidOperation

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class SectionEValidator(BaseValidator):
    """
    Validator for Section E: Class Limits.

    Rules:
        21. <MaximumOccurences> if present is an integer ≥ 1
        22. <MaximumAmount> if present is a decimal ≥ 0, no currency symbol
        23. <AppliesTo> (if present) contains zero or more <InternalCode> children
        24. Every <InternalCode> in <AppliesTo> is a non-empty string
        25. Optional <Characteristics> inside <Limits> is allowed
        26. If both MaximumOccurences and MaximumAmount absent, <Limits> may still appear
    """

    section_name = "Class Limits"
    section_id = "E"

    def validate(self) -> ValidationResult:
        """
        Execute Section E validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            code = class_elem.get("Code", "unknown")
            class_path = self.get_element_path(class_elem)

            # Find Limits element (Rule D.20 - optional)
            limits = class_elem.find("Limits")
            if limits is None:
                continue  # No limits to validate

            limits_path = f"{class_path}/Limits"

            # Rule E.21: Validate MaximumOccurences
            max_occur_elem = limits.find("MaximumOccurences")
            if max_occur_elem is not None:
                max_occur_text = self.get_text(max_occur_elem)
                if not self._validate_positive_integer(max_occur_text, min_value=1):
                    self.result.add_error(
                        rule_id="E.21",
                        message=f"<MaximumOccurences> in class '{code}' must be an integer ≥ 1, "
                        f"found '{max_occur_text}'",
                        element_path=f"{limits_path}/MaximumOccurences",
                        details={"code": code, "value": max_occur_text},
                    )

            # Rule E.22: Validate MaximumAmount
            max_amount_elem = limits.find("MaximumAmount")
            if max_amount_elem is not None:
                max_amount_text = self.get_text(max_amount_elem)
                if not self._validate_decimal(max_amount_text, min_value=0):
                    self.result.add_error(
                        rule_id="E.22",
                        message=f"<MaximumAmount> in class '{code}' must be a decimal ≥ 0 "
                        f"with no currency symbols, found '{max_amount_text}'",
                        element_path=f"{limits_path}/MaximumAmount",
                        details={"code": code, "value": max_amount_text},
                    )

            # Rules E.23 & E.24: Validate AppliesTo
            applies_to = limits.find("AppliesTo")
            if applies_to is not None:
                internal_codes = applies_to.findall("InternalCode")
                for idx, ic_elem in enumerate(internal_codes, start=1):
                    ic_text = self.get_text(ic_elem)
                    if not ic_text:
                        self.result.add_error(
                            rule_id="E.24",
                            message=f"<InternalCode> #{idx} in <AppliesTo> of class '{code}' "
                            f"must be a non-empty string",
                            element_path=f"{limits_path}/AppliesTo/InternalCode[{idx}]",
                            details={"code": code},
                        )

            # Rule E.25: Characteristics inside Limits is allowed
            # Will be validated in Section G if present

        return self.result

    def _validate_positive_integer(self, value: str, min_value: int = 0) -> bool:
        """
        Validate that a string represents a positive integer.

        Args:
            value: String to validate
            min_value: Minimum allowed value

        Returns:
            True if valid, False otherwise
        """
        if not value:
            return False

        try:
            num = int(value)
            return num >= min_value
        except ValueError:
            return False

    def _validate_decimal(self, value: str, min_value: float = 0.0) -> bool:
        """
        Validate that a string represents a valid decimal number.

        Args:
            value: String to validate
            min_value: Minimum allowed value

        Returns:
            True if valid, False otherwise
        """
        if not value:
            return False

        # Check for invalid characters (currency symbols, thousands separators, etc.)
        if any(char in value for char in ["$", "€", "£", ",", " "]):
            return False

        try:
            num = Decimal(value)
            return num >= Decimal(str(min_value))
        except (InvalidOperation, ValueError):
            return False

