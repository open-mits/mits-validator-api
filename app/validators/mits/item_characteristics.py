"""
Section G: Item Characteristics — Presence & Enumerations (Rules 42-49)

Validates the Characteristics block within offer items.
"""

from typing import Set

from xml.etree.ElementTree import Element
from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import (
    ChargeRequirement,
    Lifecycle,
    PaymentFrequency,
    Refundability,
    RefundabilityMaxType,
    RefundPerType,
    validate_enum,
)


class ItemCharacteristicsValidator(BaseValidator):
    """
    Validator for Section G: Item Characteristics.

    Rules:
        42. <ChargeRequirement> is required (Included|Mandatory|Optional|Situational|Conditional)
        43. If ChargeRequirement="Conditional", conditional scope must be present
        44. <Lifecycle> is required (At Application|Move-in|During Term|Move-out)
        45. <PaymentFrequency> is optional, must use valid enumeration
        46. <Refundability> is optional (Non-refundable|Refundable|Deposit)
        47. If Refundability ∈ {Refundable, Deposit}, RefundabilityMaxType and Max required
        48. <RefundabilityPerType> if present uses same enumeration as AmountPerType
        49. <RequirementDescription> is optional, must be non-empty if present
    """

    section_name = "Item Characteristics"
    section_id = "item_characteristics"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section G validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Collect all items for conditional reference validation (Rule 43)
        all_items_codes = self._collect_all_item_codes()

        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                characteristics = item.find("Characteristics")

                if characteristics is None:
                    continue  # Handled by Rule F.32

                char_path = f"{self.get_element_path(item)}/Characteristics"
                self._validate_characteristics(
                    characteristics, item_code, class_code, char_path, all_items_codes
                )

        return self.result

    def _collect_all_item_codes(self) -> Set[str]:
        """
        Collect all InternalCode values from all items in the document.

        Returns:
            Set of all internal codes
        """
        codes = set()
        for class_elem in self.root.iter("ChargeOfferClass"):
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]
            for item in items:
                code = item.get("InternalCode", "").strip()
                if code:
                    codes.add(code)
        return codes

    def _validate_characteristics(
        self,
        characteristics: Element,
        item_code: str,
        class_code: str,
        char_path: str,
        all_item_codes: Set[str],
    ) -> None:
        """
        Validate a Characteristics block.

        Args:
            characteristics: Characteristics element
            item_code: InternalCode of the parent item
            class_code: Code of the parent class
            char_path: Path to characteristics for error messages
            all_item_codes: Set of all valid item codes for conditional validation
        """
        # Rule G.42: ChargeRequirement is required
        charge_req_elem = characteristics.find("ChargeRequirement")
        charge_req = None
        if charge_req_elem is None:
            self.result.add_error(
                rule_id="char_requirement_required",
                message=f"Item '{item_code}' missing required <ChargeRequirement> in <Characteristics>",
                element_path=char_path,
                details={"class_code": class_code, "item_code": item_code},
            )
        else:
            charge_req = self.get_text(charge_req_elem)
            if not charge_req:
                self.result.add_error(
                    rule_id="char_requirement_required",
                    message=f"Item '{item_code}' has empty <ChargeRequirement>",
                    element_path=f"{char_path}/ChargeRequirement",
                    details={"class_code": class_code, "item_code": item_code},
                )
            else:
                # Validate enumeration
                valid, error_msg = validate_enum(charge_req, ChargeRequirement, "char_requirement_required", "ChargeRequirement")
                if not valid:
                    self.result.add_error(
                        rule_id="char_requirement_required",
                        message=error_msg,
                        element_path=f"{char_path}/ChargeRequirement",
                        details={"class_code": class_code, "item_code": item_code},
                    )

                # Rule G.43: Validate Conditional requirements
                if charge_req == "Conditional":
                    self._validate_conditional(
                        characteristics, item_code, class_code, char_path, all_item_codes
                    )

        # Rule G.44: Lifecycle is required
        lifecycle_elem = characteristics.find("Lifecycle")
        if lifecycle_elem is None:
            self.result.add_error(
                rule_id="char_lifecycle_required",
                message=f"Item '{item_code}' missing required <Lifecycle> in <Characteristics>",
                element_path=char_path,
                details={"class_code": class_code, "item_code": item_code},
            )
        else:
            lifecycle = self.get_text(lifecycle_elem)
            if not lifecycle:
                self.result.add_error(
                    rule_id="char_lifecycle_required",
                    message=f"Item '{item_code}' has empty <Lifecycle>",
                    element_path=f"{char_path}/Lifecycle",
                    details={"class_code": class_code, "item_code": item_code},
                )
            else:
                valid, error_msg = validate_enum(lifecycle, Lifecycle, "char_lifecycle_required", "Lifecycle")
                if not valid:
                    self.result.add_error(
                        rule_id="char_lifecycle_required",
                        message=error_msg,
                        element_path=f"{char_path}/Lifecycle",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rule G.45: PaymentFrequency optional, must be valid
        freq_elem = characteristics.find("PaymentFrequency")
        if freq_elem is not None:
            freq = self.get_text(freq_elem)
            if freq:
                valid, error_msg = validate_enum(freq, PaymentFrequency, "char_frequency_valid", "PaymentFrequency")
                if not valid:
                    self.result.add_error(
                        rule_id="char_frequency_valid",
                        message=error_msg,
                        element_path=f"{char_path}/PaymentFrequency",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rules G.46 & G.47: Validate Refundability
        self._validate_refundability(characteristics, item_code, class_code, char_path)

        # Rule G.49: RequirementDescription optional, must be non-empty if present
        req_desc_elem = characteristics.find("RequirementDescription")
        if req_desc_elem is not None:
            req_desc = self.get_text(req_desc_elem)
            if req_desc and not req_desc.strip():
                self.result.add_error(
                    rule_id="char_requirement_desc_nonempty",
                    message=f"Item '{item_code}' has whitespace-only <RequirementDescription>",
                    element_path=f"{char_path}/RequirementDescription",
                    details={"class_code": class_code, "item_code": item_code},
                )

    def _validate_conditional(
        self,
        characteristics: Element,
        item_code: str,
        class_code: str,
        char_path: str,
        all_item_codes: Set[str],
    ) -> None:
        """
        Validate Rule G.43: Conditional ChargeRequirement requirements.

        Args:
            characteristics: Characteristics element
            item_code: InternalCode of the parent item
            class_code: Code of the parent class
            char_path: Path to characteristics for error messages
            all_item_codes: Set of all valid item codes
        """
        # Rule G.43.1: Must have ConditionalInternalCode or ConditionalScope
        cond_codes_elem = characteristics.find("ConditionalInternalCode")
        cond_scope_elem = characteristics.find("ConditionalScope")
        
        # Try to get codes from either structure
        cond_code_text = None
        if cond_codes_elem is not None:
            cond_code_text = self.get_text(cond_codes_elem)
        elif cond_scope_elem is not None:
            # Handle ConditionalScope/InternalCode structure
            internal_codes = cond_scope_elem.findall("InternalCode")
            if internal_codes:
                cond_code_text = " ".join(self.get_text(ic) for ic in internal_codes if self.get_text(ic))

        if not cond_code_text:
            self.result.add_error(
                rule_id="char_conditional_has_codes",
                message=f"Item '{item_code}' has ChargeRequirement='Conditional' but no valid conditional codes",
                element_path=char_path,
                details={"class_code": class_code, "item_code": item_code},
            )
            return

        # Split by comma or whitespace to handle multiple codes
        referenced_codes = [c.strip() for c in cond_code_text.replace(",", " ").split() if c.strip()]

        for ref_code in referenced_codes:
            # Rule G.43.3: No self-reference
            if ref_code == item_code:
                self.result.add_error(
                    rule_id="char_no_self_reference",
                    message=f"Item '{item_code}' cannot be conditional on itself",
                    element_path=f"{char_path}/ConditionalInternalCode",
                    details={"class_code": class_code, "item_code": item_code},
                )
                continue

            # Rule G.43.2: Code must exist in document
            if ref_code not in all_item_codes:
                self.result.add_error(
                    rule_id="char_conditional_code_exists",
                    message=f"Item '{item_code}' references non-existent code '{ref_code}' in <ConditionalInternalCode>",
                    element_path=f"{char_path}/ConditionalInternalCode",
                    details={
                        "class_code": class_code,
                        "item_code": item_code,
                        "referenced_code": ref_code,
                    },
                )

        # Rule G.43.4: No cyclic references (checked separately in Section N)

    def _validate_refundability(
        self, characteristics: Element, item_code: str, class_code: str, char_path: str
    ) -> None:
        """
        Validate Rules G.46 & G.47: Refundability requirements.

        Args:
            characteristics: Characteristics element
            item_code: InternalCode of the parent item
            class_code: Code of the parent class
            char_path: Path to characteristics for error messages
        """
        refund_elem = characteristics.find("Refundability")
        if refund_elem is None:
            return  # Optional field

        refund = self.get_text(refund_elem)
        if not refund:
            return  # Empty is allowed

        # Rule G.46: Validate enumeration
        valid, error_msg = validate_enum(refund, Refundability, "char_refundability_valid", "Refundability")
        if not valid:
            self.result.add_error(
                rule_id="char_refundability_valid",
                message=error_msg,
                element_path=f"{char_path}/Refundability",
                details={"class_code": class_code, "item_code": item_code},
            )
            return

        # Rule G.47: If Refundable or Deposit, check for required fields
        if refund in ["Refundable", "Deposit"]:
            # Check for RefundDetails container
            refund_details = characteristics.find("RefundDetails")
            if refund_details is None:
                self.result.add_error(
                    rule_id="char_refund_details_required",
                    message=f"Item '{item_code}' has Refundability='{refund}' but missing <RefundDetails> element",
                    element_path=char_path,
                    details={"class_code": class_code, "item_code": item_code},
                )
                return
            
            details_path = f"{char_path}/RefundDetails"
            
            # Rule G.47.1: RefundMaxType required
            max_type_elem = refund_details.find("RefundMaxType")
            if max_type_elem is None:
                # Also check for RefundabilityMaxType (alternate naming)
                max_type_elem = characteristics.find("RefundabilityMaxType")
            
            if max_type_elem is None:
                self.result.add_error(
                    rule_id="char_refund_max_type_required",
                    message=f"Item '{item_code}' has Refundability='{refund}' but missing <RefundabilityMaxType>",
                    element_path=char_path,
                    details={"class_code": class_code, "item_code": item_code},
                )
            else:
                max_type = self.get_text(max_type_elem)
                if not max_type:
                    self.result.add_error(
                        rule_id="char_refund_max_type_required",
                        message=f"Item '{item_code}' has empty <RefundabilityMaxType>",
                        element_path=f"{char_path}/RefundabilityMaxType",
                        details={"class_code": class_code, "item_code": item_code},
                    )
                else:
                    valid, error_msg = validate_enum(
                        max_type, RefundabilityMaxType, "char_refund_max_type_required", "RefundabilityMaxType"
                    )
                    if not valid:
                        self.result.add_error(
                            rule_id="char_refund_max_type_required",
                            message=error_msg,
                            element_path=f"{char_path}/RefundabilityMaxType",
                            details={"class_code": class_code, "item_code": item_code},
                        )

            # Rule G.47.2: RefundMax required and decimal ≥ 0
            max_elem = refund_details.find("RefundMax")
            if max_elem is None:
                # Also check for RefundabilityMax (alternate naming)
                max_elem = characteristics.find("RefundabilityMax")
            
            if max_elem is None:
                self.result.add_error(
                    rule_id="char_refund_max_required",
                    message=f"Item '{item_code}' has Refundability='{refund}' but missing <RefundabilityMax>",
                    element_path=char_path,
                    details={"class_code": class_code, "item_code": item_code},
                )
            else:
                max_val = self.get_text(max_elem)
                if not max_val:
                    self.result.add_error(
                        rule_id="char_refund_max_required",
                        message=f"Item '{item_code}' has empty <RefundabilityMax>",
                        element_path=f"{char_path}/RefundabilityMax",
                        details={"class_code": class_code, "item_code": item_code},
                    )
                else:
                    try:
                        from decimal import Decimal

                        val = Decimal(max_val)
                        if val < 0:
                            self.result.add_error(
                                rule_id="char_refund_max_required",
                                message=f"Item '{item_code}' <RefundabilityMax> must be ≥ 0, found '{max_val}'",
                                element_path=f"{char_path}/RefundabilityMax",
                                details={"class_code": class_code, "item_code": item_code},
                            )
                    except Exception:
                        self.result.add_error(
                            rule_id="char_refund_max_required",
                            message=f"Item '{item_code}' <RefundabilityMax> must be a valid decimal, found '{max_val}'",
                            element_path=f"{char_path}/RefundabilityMax",
                            details={"class_code": class_code, "item_code": item_code},
                        )
            
            # Rule G.47.3: RefundPerType validation (optional but if present must be valid)
            per_type_elem = refund_details.find("RefundPerType")
            if per_type_elem is not None:
                per_type = self.get_text(per_type_elem)
                if per_type:
                    valid, error_msg = validate_enum(
                        per_type, RefundPerType, "char_refund_per_type_valid", "RefundPerType"
                    )
                    if not valid:
                        self.result.add_error(
                            rule_id="char_refund_per_type_valid",
                            message=error_msg,
                            element_path=f"{details_path}/RefundPerType",
                            details={"class_code": class_code, "item_code": item_code},
                        )

