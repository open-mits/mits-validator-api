"""
Section H: Amount Basis & Per-Item Semantics (Rules 50-56)

Validates AmountBasis field and its relationship with amount blocks.
"""

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import AmountBasis, validate_enum


class AmountBasisValidator(BaseValidator):
    """
    Validator for Section H: Amount Basis.

    Rules:
        50. <AmountBasis> enumeration must be valid (Explicit|Percentage Of|Within Range|Stepped|Variable)
        51. If AmountBasis="Explicit", each amount must have Amounts (≥1), Percentage empty
        52. If AmountBasis="Percentage Of", Percentage present, Amounts empty, PercentageOfCode present
        53. If AmountBasis="Within Range", accepts one Amounts value per block
        54. If AmountBasis="Stepped", each amount block must have ≥2 Amounts values
        55. If AmountBasis="Variable", amount block must have either Amounts OR Percentage
        56. If ChargeRequirement="Included", AmountBasis must be empty, all amounts empty
    """

    section_name = "Amount Basis"
    section_id = "amount_basis"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section H validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_item_amount_basis(item, item_code, class_code)

        return self.result

    def _validate_item_amount_basis(
        self, item: Element, item_code: str, class_code: str
    ) -> None:
        """
        Validate AmountBasis for a single item.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
        """
        item_path = f"{self.get_element_path(item)}"

        # Get ChargeRequirement to check for "Included" (Rule H.56)
        characteristics = item.find("Characteristics")
        charge_requirement = ""
        if characteristics is not None:
            charge_req_elem = characteristics.find("ChargeRequirement")
            if charge_req_elem is not None:
                charge_requirement = self.get_text(charge_req_elem)

        # Get AmountBasis
        amount_basis_elem = item.find("AmountBasis")
        amount_basis = self.get_text(amount_basis_elem) if amount_basis_elem is not None else ""

        # Rule H.56: If ChargeRequirement="Included", AmountBasis must be empty
        if charge_requirement == "Included":
            if amount_basis:
                self.result.add_error(
                    rule_id="basis_included_empty",
                    message=f"Item '{item_code}' has ChargeRequirement='Included' but non-empty AmountBasis='{amount_basis}'. "
                    f"AmountBasis must be empty for Included items",
                    element_path=f"{item_path}/AmountBasis",
                    details={"class_code": class_code, "item_code": item_code},
                )

            # Validate all amount blocks are empty (checked in more detail in Rule H.56.2/3)
            amount_blocks = item.findall("ChargeOfferAmount")
            for idx, block in enumerate(amount_blocks, start=1):
                self._validate_included_amount_empty(block, item_code, class_code, item_path, idx)

            return  # Skip other amount basis validation for Included items

        # Rule H.50: Validate AmountBasis enumeration (if not empty)
        if amount_basis:
            valid, error_msg = validate_enum(amount_basis, AmountBasis, "basis_enum_valid", "AmountBasis")
            if not valid:
                self.result.add_error(
                    rule_id="basis_enum_valid",
                    message=error_msg,
                    element_path=f"{item_path}/AmountBasis",
                    details={"class_code": class_code, "item_code": item_code},
                )
                return  # Can't validate basis rules if basis is invalid

        # Rule H.37: AmountBasis can only be empty if ChargeRequirement="Included"
        if not amount_basis and charge_requirement != "Included":
            self.result.add_error(
                rule_id="item_amount_basis_required",
                message=f"Item '{item_code}' has empty AmountBasis but ChargeRequirement='{charge_requirement}'. "
                f"AmountBasis can only be empty if ChargeRequirement='Included'",
                element_path=f"{item_path}/AmountBasis",
                details={"class_code": class_code, "item_code": item_code},
            )
            return

        # Rules H.51-55: Validate amount blocks against basis
        amount_blocks = item.findall("ChargeOfferAmount")
        for idx, block in enumerate(amount_blocks, start=1):
            # Get PercentageOfCode from the amount block
            percentage_of_code_elem = block.find("PercentageOfCode")
            percentage_of_code = self.get_text(percentage_of_code_elem) if percentage_of_code_elem is not None else ""
            
            # Rule H.38: PercentageOfCode present only when AmountBasis="Percentage Of"
            if percentage_of_code and amount_basis != "Percentage Of":
                self.result.add_error(
                    rule_id="item_percentage_code_when_needed",
                    message=f"Item '{item_code}' has <PercentageOfCode> but AmountBasis='{amount_basis}'. "
                    f"PercentageOfCode should only be present when AmountBasis='Percentage Of'",
                    element_path=f"{item_path}/ChargeOfferAmount[{idx}]/PercentageOfCode",
                    details={"class_code": class_code, "item_code": item_code},
                )
            
            self._validate_amount_block_for_basis(
                block, amount_basis, item_code, class_code, item_path, idx, percentage_of_code
            )

    def _validate_included_amount_empty(
        self, block: Element, item_code: str, class_code: str, item_path: str, block_idx: int
    ) -> None:
        """
        Validate Rule H.56.2/3: Included items must have empty amounts and percentages.

        Args:
            block: ChargeOfferAmount element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
            block_idx: Index of the amount block
        """
        block_path = f"{item_path}/ChargeOfferAmount[{block_idx}]"

        # Check Amounts
        amounts_elem = block.find("Amounts")
        if amounts_elem is not None:
            amounts_text = self.get_text(amounts_elem)
            if amounts_text:
                self.result.add_error(
                    rule_id="basis_included_amounts_empty",
                    message=f"Item '{item_code}' has ChargeRequirement='Included' but non-empty <Amounts>='{amounts_text}'. "
                    f"All amounts must be empty for Included items",
                    element_path=f"{block_path}/Amounts",
                    details={"class_code": class_code, "item_code": item_code},
                )

        # Check Percentage
        percentage_elem = block.find("Percentage")
        if percentage_elem is not None:
            percentage_text = self.get_text(percentage_elem)
            if percentage_text:
                self.result.add_error(
                    rule_id="basis_included_percentage_empty",
                    message=f"Item '{item_code}' has ChargeRequirement='Included' but non-empty <Percentage>='{percentage_text}'. "
                    f"All percentages must be empty for Included items",
                    element_path=f"{block_path}/Percentage",
                    details={"class_code": class_code, "item_code": item_code},
                )

    def _validate_amount_block_for_basis(
        self,
        block: Element,
        amount_basis: str,
        item_code: str,
        class_code: str,
        item_path: str,
        block_idx: int,
        percentage_of_code: str,
    ) -> None:
        """
        Validate an amount block against the item's AmountBasis.

        Args:
            block: ChargeOfferAmount element
            amount_basis: AmountBasis value
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
            block_idx: Index of the amount block
            percentage_of_code: PercentageOfCode value
        """
        block_path = f"{item_path}/ChargeOfferAmount[{block_idx}]"

        percentage_elem = block.find("Percentage")
        percentage_text = self.get_text(percentage_elem) if percentage_elem is not None else ""

        # Count number of amount values
        # Can be: multiple <Amounts> elements, or comma/newline-separated values within one element
        amounts_elems = block.findall("Amounts")
        amount_count = 0
        amounts_text = ""  # Initialize to avoid UnboundLocalError
        
        if amounts_elems:
            # First check if there are multiple <Amounts> elements
            amount_count = len(amounts_elems)
            
            # If only one element, check if it contains comma-separated values
            if amount_count == 1:
                amounts_text = self.get_text(amounts_elems[0])
                if amounts_text:
                    # Handle multiple amounts separated by commas or newlines
                    amount_values = [
                        a.strip()
                        for a in amounts_text.replace("\n", ",").replace("\t", ",").split(",")
                        if a.strip()
                    ]
                    amount_count = len(amount_values)
                else:
                    amount_count = 0
            
            # If multiple elements, collect text from all for validation purposes
            elif amount_count > 1:
                amounts_text = ", ".join([self.get_text(elem) for elem in amounts_elems if self.get_text(elem)])

        if amount_basis == "Explicit":
            # Rule H.51.1: Must have Amounts (≥1)
            if amount_count == 0:
                self.result.add_error(
                    rule_id="basis_explicit_amounts_nonempty",
                    message=f"Item '{item_code}' has AmountBasis='Explicit' but empty <Amounts>. "
                    f"At least one amount value is required",
                    element_path=f"{block_path}/Amounts",
                    details={"class_code": class_code, "item_code": item_code},
                )

            # Rule H.51.2: Percentage must be empty
            if percentage_text:
                self.result.add_error(
                    rule_id="basis_explicit_percentage_empty",
                    message=f"Item '{item_code}' has AmountBasis='Explicit' but non-empty <Percentage>='{percentage_text}'. "
                    f"Percentage must be empty for Explicit basis",
                    element_path=f"{block_path}/Percentage",
                    details={"class_code": class_code, "item_code": item_code},
                )

        elif amount_basis == "Percentage Of":
            # Rule H.52.1: Percentage must be present
            if not percentage_text:
                self.result.add_error(
                    rule_id="basis_percentage_has_value",
                    message=f"Item '{item_code}' has AmountBasis='Percentage Of' but empty <Percentage>. "
                    f"Percentage value is required",
                    element_path=f"{block_path}/Percentage",
                    details={"class_code": class_code, "item_code": item_code},
                )

            # Rule H.52.2: Amounts must be empty
            if amounts_text:
                self.result.add_error(
                    rule_id="basis_percentage_amounts_empty",
                    message=f"Item '{item_code}' has AmountBasis='Percentage Of' but non-empty <Amounts>='{amounts_text}'. "
                    f"Amounts must be empty for Percentage Of basis",
                    element_path=f"{block_path}/Amounts",
                    details={"class_code": class_code, "item_code": item_code},
                )

            # Rule H.52.3: PercentageOfCode must be present
            if not percentage_of_code:
                self.result.add_error(
                    rule_id="basis_percentage_has_code",
                    message=f"Item '{item_code}' has AmountBasis='Percentage Of' but empty <PercentageOfCode>. "
                    f"PercentageOfCode is required to reference the target item",
                    element_path=f"{item_path}/PercentageOfCode",
                    details={"class_code": class_code, "item_code": item_code},
                )
            
            # Rule H.52.4: No circular reference (item cannot reference itself)
            elif percentage_of_code == item_code:
                self.result.add_error(
                    rule_id="basis_percentage_no_circular",
                    message=f"Item '{item_code}' has AmountBasis='Percentage Of' with <PercentageOfCode>='{percentage_of_code}'. "
                    f"An item cannot reference itself",
                    element_path=f"{item_path}/PercentageOfCode",
                    details={"class_code": class_code, "item_code": item_code},
                )

        elif amount_basis in ("Within Range", "Range or Variable"):
            # Rule H.53.1: Within Range requires exactly two separate <Amounts> elements
            # First element is the lowest amount, second element is the highest amount
            # Comma-separated or dash-separated values in a single element are NOT allowed
            amounts_element_count = len(amounts_elems) if amounts_elems else 0
            if amounts_element_count != 2:
                if amounts_element_count == 0:
                    self.result.add_error(
                        rule_id="basis_range_one_amount",
                        message=f"Item '{item_code}' has AmountBasis='{amount_basis}' but no <Amounts> elements. "
                        f"Within Range requires exactly two separate <Amounts> elements (lowest and highest)",
                        element_path=f"{block_path}/Amounts",
                        details={"class_code": class_code, "item_code": item_code, "count": amounts_element_count},
                    )
                elif amounts_element_count == 1:
                    self.result.add_error(
                        rule_id="basis_range_one_amount",
                        message=f"Item '{item_code}' has AmountBasis='{amount_basis}' but only {amounts_element_count} <Amounts> element. "
                        f"Within Range requires exactly two separate <Amounts> elements (first is lowest, second is highest)",
                        element_path=f"{block_path}/Amounts",
                        details={"class_code": class_code, "item_code": item_code, "count": amounts_element_count},
                    )
                else:
                    self.result.add_error(
                        rule_id="basis_range_one_amount",
                        message=f"Item '{item_code}' has AmountBasis='{amount_basis}' but {amounts_element_count} <Amounts> elements. "
                        f"Within Range requires exactly two separate <Amounts> elements (first is lowest, second is highest)",
                        element_path=f"{block_path}/Amounts",
                        details={"class_code": class_code, "item_code": item_code, "count": amounts_element_count},
                    )

        elif amount_basis == "Stepped":
            # Rule H.54.1: Must have ≥2 Amounts values
            if amount_count < 2:
                self.result.add_error(
                    rule_id="basis_stepped_min_two",
                    message=f"Item '{item_code}' has AmountBasis='Stepped' but only {amount_count} amount value(s). "
                    f"At least 2 amount values are required for Stepped pricing",
                    element_path=f"{block_path}/Amounts",
                    details={"class_code": class_code, "item_code": item_code, "count": amount_count},
                )

        elif amount_basis == "Variable":
            # Rule H.55.1: Must have either Amounts OR Percentage (not both, not neither)
            has_amounts = bool(amounts_text)
            has_percentage = bool(percentage_text)

            if not has_amounts and not has_percentage:
                self.result.add_error(
                    rule_id="basis_variable_not_both",
                    message=f"Item '{item_code}' has AmountBasis='Variable' but both <Amounts> and <Percentage> are empty. "
                    f"Variable basis requires either Amounts OR Percentage",
                    element_path=block_path,
                    details={"class_code": class_code, "item_code": item_code},
                )
            elif has_amounts and has_percentage:
                self.result.add_error(
                    rule_id="basis_variable_not_both",
                    message=f"Item '{item_code}' has AmountBasis='Variable' but both <Amounts> and <Percentage> are present. "
                    f"Variable basis requires either Amounts OR Percentage, not both",
                    element_path=block_path,
                    details={"class_code": class_code, "item_code": item_code},
                )

