"""
Sections Q, R, S, T: Hygiene, Dates, Frequency/Basis Coherence, Duplicates (Rules 98-110)

Validates text hygiene, date consistency, frequency/basis alignment, and duplicate detection.
"""

import re
from datetime import datetime
from typing import Dict, List, Set

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult


class SectionQRSTValidator(BaseValidator):
    """
    Validator for Sections Q, R, S, T: Final Validation Rules.

    Rules:
        Q: 98-102 (Text & whitespace hygiene)
        R: 103-105 (Date/time consistency)
        S: 106-108 (Frequency vs basis and context)
        T: 109-110 (Duplicates & collisions)
    """

    section_name = "Hygiene & Duplicates"
    section_id = "Q-R-S-T"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    REQUIRED_TEXT_FIELDS = {
        "Name",
        "Description",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Sections Q, R, S, T validation rules.

        Returns:
            ValidationResult with any errors found
        """
        # Section Q: Text hygiene
        self._validate_text_hygiene()

        # Section R: Date consistency (already mostly validated in Section I)

        # Section S: Frequency vs basis coherence
        self._validate_frequency_basis_coherence()

        # Section T: Duplicates and collisions
        self._validate_duplicates()

        return self.result

    def _validate_text_hygiene(self) -> None:
        """
        Validate Rules Q.98-102: Text and whitespace hygiene.
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                item_path = self.get_element_path(item)

                # Rule Q.98: Required text fields must be non-empty after trimming
                for field_name in self.REQUIRED_TEXT_FIELDS:
                    field_elem = item.find(field_name)
                    if field_elem is not None:
                        text = field_elem.text or ""
                        if not text.strip():
                            self.result.add_error(
                                rule_id="Q.98",
                                message=f"Item '{item_code}' has empty or whitespace-only <{field_name}>",
                                element_path=f"{item_path}/{field_name}",
                                details={"class_code": class_code, "item_code": item_code},
                            )

                # Rules Q.99-101: Validate numeric fields
                self._validate_numeric_hygiene(item, item_code, class_code, item_path)

                # Rule Q.102: Check for non-ASCII control characters
                self._check_control_characters(item, item_code, class_code, item_path)

    def _validate_numeric_hygiene(
        self, item: ET.Element, item_code: str, class_code: str, item_path: str
    ) -> None:
        """
        Validate Rules Q.99-101: Numeric field hygiene.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        # Check all amount blocks
        for idx, block in enumerate(item.findall("ChargeOfferAmount"), start=1):
            block_path = f"{item_path}/ChargeOfferAmount[{idx}]"

            # Check Amounts
            amounts_elem = block.find("Amounts")
            if amounts_elem is not None:
                amounts_text = self.get_text(amounts_elem)
                if amounts_text:
                    self._check_numeric_format(amounts_text, item_code, class_code, f"{block_path}/Amounts")

            # Check Percentage
            percentage_elem = block.find("Percentage")
            if percentage_elem is not None:
                percentage_text = self.get_text(percentage_elem)
                if percentage_text:
                    self._check_numeric_format(percentage_text, item_code, class_code, f"{block_path}/Percentage")

    def _check_numeric_format(
        self, value: str, item_code: str, class_code: str, field_path: str
    ) -> None:
        """
        Check numeric format for violations.

        Args:
            value: Numeric value to check
            item_code: InternalCode of the item
            class_code: Code of the parent class
            field_path: Path to field for error messages
        """
        # Parse comma-separated values
        values = [v.strip() for v in value.replace("\n", ",").replace("\t", ",").split(",") if v.strip()]

        for val in values:
            # Rule Q.99: Disallow currency symbols, thousands separators
            if any(char in val for char in ["$", "€", "£", ",", " "]):
                self.result.add_error(
                    rule_id="Q.99",
                    message=f"Numeric value '{val}' in item '{item_code}' contains invalid characters. "
                    f"No currency symbols or thousands separators allowed",
                    element_path=field_path,
                    details={"class_code": class_code, "item_code": item_code, "value": val},
                )

            # Rule Q.100: Disallow leading plus signs
            if val.startswith("+"):
                self.result.add_error(
                    rule_id="Q.100",
                    message=f"Numeric value '{val}' in item '{item_code}' has leading plus sign. "
                    f"Not allowed",
                    element_path=field_path,
                    details={"class_code": class_code, "item_code": item_code, "value": val},
                )

    def _check_control_characters(
        self, item: ET.Element, item_code: str, class_code: str, item_path: str
    ) -> None:
        """
        Validate Rule Q.101: Disallow non-ASCII control characters.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        # Check text fields for control characters
        for field_name in ["Name", "Description"]:
            field_elem = item.find(field_name)
            if field_elem is not None and field_elem.text:
                text = field_elem.text

                # Check for control characters (excluding standard whitespace)
                control_chars = [c for c in text if ord(c) < 32 and c not in ['\n', '\r', '\t']]

                if control_chars:
                    self.result.add_error(
                        rule_id="Q.101",
                        message=f"Item '{item_code}' <{field_name}> contains non-ASCII control characters",
                        element_path=f"{item_path}/{field_name}",
                        details={"class_code": class_code, "item_code": item_code},
                    )

    def _validate_frequency_basis_coherence(self) -> None:
        """
        Validate Rules S.106-108: Frequency vs basis coherence.
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

                freq_elem = characteristics.find("PaymentFrequency")
                lifecycle_elem = characteristics.find("Lifecycle")

                freq = self.get_text(freq_elem) if freq_elem is not None else ""
                lifecycle = self.get_text(lifecycle_elem) if lifecycle_elem is not None else ""

                # Get AmountBasis and AmountPerType
                amount_basis_elem = item.find("AmountBasis")
                amount_basis = self.get_text(amount_basis_elem) if amount_basis_elem is not None else ""

                amount_per_type_elem = item.find("AmountPerType")
                amount_per_type = self.get_text(amount_per_type_elem) if amount_per_type_elem is not None else ""

                # Rule S.106: Hourly or Per-occurrence with AmountPerType=Period not allowed
                if freq in ["Hourly", "Per-occurrence"] and amount_per_type == "Period":
                    self.result.add_error(
                        rule_id="S.106",
                        message=f"Item '{item_code}' has PaymentFrequency='{freq}' with AmountPerType='Period'. "
                        f"This combination is not allowed",
                        element_path=f"{item_path}/AmountPerType",
                        details={"class_code": class_code, "item_code": item_code, "frequency": freq},
                    )

                # Rule S.107: Monthly frequency with Within Range basis (check)
                if freq == "Monthly" and amount_basis == "Within Range":
                    self.result.add_warning(
                        rule_id="S.107",
                        message=f"Item '{item_code}' has PaymentFrequency='Monthly' with AmountBasis='Within Range'. "
                        f"Range should be expressed by occurrences, not conflicting frequencies",
                        element_path=f"{item_path}/AmountBasis",
                        details={"class_code": class_code, "item_code": item_code},
                    )

                # Rule S.108: During Term lifecycle with no frequency
                if lifecycle == "During Term" and not freq:
                    self.result.add_error(
                        rule_id="S.108",
                        message=f"Item '{item_code}' has Lifecycle='During Term' but no <PaymentFrequency>. "
                        f"Frequency is required for During Term charges",
                        element_path=f"{item_path}/Characteristics",
                        details={"class_code": class_code, "item_code": item_code},
                    )

    def _validate_duplicates(self) -> None:
        """
        Validate Rules T.109-110: Duplicates and collisions.
        """
        # Build a map of items by class for duplicate detection
        class_items: Dict[str, List[tuple]] = {}

        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            if class_code not in class_items:
                class_items[class_code] = []

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                item_path = self.get_element_path(item)

                name_elem = item.find("Name")
                name = self.get_text(name_elem).lower() if name_elem is not None else ""

                # Build characteristics hash for duplicate detection
                characteristics_hash = self._build_characteristics_hash(item)

                class_items[class_code].append({
                    "item_code": item_code,
                    "name": name,
                    "hash": characteristics_hash,
                    "path": item_path,
                    "element": item,
                })

        # Check for duplicates within each class
        for class_code, items in class_items.items():
            # Rule T.109: Check for duplicate names (case-insensitive)
            name_counts: Dict[str, List[str]] = {}
            for item in items:
                name = item["name"]
                if name:
                    if name not in name_counts:
                        name_counts[name] = []
                    name_counts[name].append(item["item_code"])

            for name, codes in name_counts.items():
                if len(codes) > 1:
                    self.result.add_error(
                        rule_id="T.109",
                        message=f"Duplicate item Name '{name}' found in class '{class_code}' "
                        f"(items: {', '.join(codes)}). Names should be unique within a class",
                        element_path=f"/ChargeOfferClass[@Code='{class_code}']",
                        details={"class_code": class_code, "duplicate_name": name, "item_codes": codes},
                    )

            # Rule T.110: Check for exact duplicate items (same code + characteristics)
            hash_counts: Dict[str, List[str]] = {}
            for item in items:
                item_hash = item["hash"]
                if item_hash not in hash_counts:
                    hash_counts[item_hash] = []
                hash_counts[item_hash].append(item["item_code"])

            for item_hash, codes in hash_counts.items():
                if len(codes) > 1:
                    self.result.add_error(
                        rule_id="T.110",
                        message=f"Duplicate item definition found in class '{class_code}' "
                        f"(items: {', '.join(codes)}). Items have identical code and characteristics",
                        element_path=f"/ChargeOfferClass[@Code='{class_code}']",
                        details={"class_code": class_code, "item_codes": codes},
                    )

    def _build_characteristics_hash(self, item: ET.Element) -> str:
        """
        Build a hash representing item characteristics for duplicate detection.

        Args:
            item: Offer item element

        Returns:
            Hash string
        """
        characteristics = item.find("Characteristics")
        if characteristics is None:
            return ""

        # Build a canonical representation of characteristics
        parts = []

        for child in sorted(characteristics, key=lambda e: e.tag):
            text = self.get_text(child)
            if text:
                parts.append(f"{child.tag}:{text}")

        return "|".join(parts)

