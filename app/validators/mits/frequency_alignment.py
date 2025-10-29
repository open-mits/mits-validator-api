"""
Section J: AmountPerType & Frequency Alignment (Rules 66-69)

Validates AmountPerType field and its relationship with PaymentFrequency.
"""

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import AmountPerType, validate_enum


class FrequencyAlignmentValidator(BaseValidator):
    """
    Validator for Section J: AmountPerType & Frequency Alignment.

    Rules:
        66. <AmountPerType> must be one of: Item|Applicant|Leaseholder|Person|Period
        67. If AmountPerType=Applicant, note multiplicity by applicants (informational)
        68. Recurring frequency + Percentage Of one-time code is inconsistent
        69. One-time/Per-occurrence/Hourly frequency with TermBasis is valid
    """

    section_name = "AmountPerType & Frequency"
    section_id = "frequency_alignment"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    RECURRING_FREQUENCIES = {"Monthly", "Quarterly", "Annually"}
    ONE_TIME_FREQUENCIES = {"One-time", "Per-occurrence", "Hourly"}

    def validate(self) -> ValidationResult:
        """
        Execute Section J validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Collect all items with their frequencies for cross-validation
        item_info = self._collect_item_info()

        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_item_frequency(item, item_code, class_code, item_info)

        return self.result

    def _collect_item_info(self) -> dict:
        """
        Collect information about all items for cross-validation.

        Returns:
            Dict mapping item_code to (frequency, amount_basis, percentage_of_code)
        """
        info = {}

        for class_elem in self.root.iter("ChargeOfferClass"):
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "").strip()
                if not item_code:
                    continue

                characteristics = item.find("Characteristics")
                frequency = ""
                if characteristics is not None:
                    freq_elem = characteristics.find("PaymentFrequency")
                    if freq_elem is not None:
                        frequency = self.get_text(freq_elem)

                amount_basis_elem = item.find("AmountBasis")
                amount_basis = self.get_text(amount_basis_elem) if amount_basis_elem is not None else ""

                percentage_of_code_elem = item.find("PercentageOfCode")
                percentage_of_code = (
                    self.get_text(percentage_of_code_elem) if percentage_of_code_elem is not None else ""
                )

                info[item_code] = (frequency, amount_basis, percentage_of_code)

        return info

    def _validate_item_frequency(
        self, item: Element, item_code: str, class_code: str, item_info: dict
    ) -> None:
        """
        Validate frequency-related rules for a single item.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_info: Dict of all item information
        """
        item_path = self.get_element_path(item)

        # Rule J.66: Validate AmountPerType enumeration
        amount_per_type_elem = item.find("AmountPerType")
        if amount_per_type_elem is not None:
            amount_per_type = self.get_text(amount_per_type_elem)
            if amount_per_type:
                valid, error_msg = validate_enum(amount_per_type, AmountPerType, "amount_per_type_enum", "AmountPerType")
                if not valid:
                    self.result.add_error(
                        rule_id="amount_per_type_enum",
                        message=error_msg,
                        element_path=f"{item_path}/AmountPerType",
                        details={"class_code": class_code, "item_code": item_code},
                    )

                # Rule J.67: Informational note for Applicant multiplicity
                if amount_per_type == "Applicant":
                    self.result.add_info(
                        rule_id="amount_per_applicant_note",
                        message=f"Item '{item_code}' uses AmountPerType='Applicant'. "
                        f"The amount will be multiplied by the number of applicants",
                        element_path=f"{item_path}/AmountPerType",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Get frequency and amount basis for Rules J.68 & J.69
        characteristics = item.find("Characteristics")
        frequency = ""
        if characteristics is not None:
            freq_elem = characteristics.find("PaymentFrequency")
            if freq_elem is not None:
                frequency = self.get_text(freq_elem)

        amount_basis_elem = item.find("AmountBasis")
        amount_basis = self.get_text(amount_basis_elem) if amount_basis_elem is not None else ""

        percentage_of_code_elem = item.find("PercentageOfCode")
        percentage_of_code = (
            self.get_text(percentage_of_code_elem) if percentage_of_code_elem is not None else ""
        )

        # Rule J.68: Recurring frequency + Percentage Of one-time code is inconsistent
        if frequency in self.RECURRING_FREQUENCIES and amount_basis == "Percentage Of" and percentage_of_code:
            # Check if the referenced code has a one-time frequency
            if percentage_of_code in item_info:
                ref_frequency, _, _ = item_info[percentage_of_code]
                if ref_frequency in self.ONE_TIME_FREQUENCIES:
                    self.result.add_error(
                        rule_id="frequency_basis_coherent",
                        message=f"Item '{item_code}' has recurring PaymentFrequency='{frequency}' "
                        f"but references one-time item '{percentage_of_code}' (PaymentFrequency='{ref_frequency}'). "
                        f"This creates inconsistent billing semantics",
                        element_path=f"{item_path}/PercentageOfCode",
                        details={
                            "class_code": class_code,
                            "item_code": item_code,
                            "frequency": frequency,
                            "referenced_code": percentage_of_code,
                            "referenced_frequency": ref_frequency,
                        },
                    )

        # Rule J.69: One-time/Per-occurrence/Hourly with TermBasis is valid (informational)
        if frequency in self.ONE_TIME_FREQUENCIES:
            # Check if any amount blocks have TermBasis
            for block in item.findall("ChargeOfferAmount"):
                term_basis_elem = block.find("TermBasis")
                if term_basis_elem is not None and self.get_text(term_basis_elem):
                    self.result.add_info(
                        rule_id="onetime_with_term_basis",
                        message=f"Item '{item_code}' has one-time PaymentFrequency='{frequency}' with TermBasis. "
                        f"This is allowed",
                        element_path=f"{item_path}/ChargeOfferAmount/TermBasis",
                        details={"class_code": class_code, "item_code": item_code, "frequency": frequency},
                    )
                    break  # Only report once per item

