"""
Section I: Amount Blocks — Numeric/Date Formats and Term Context (Rules 57-65)

Validates the content and format of ChargeOfferAmount blocks.
"""

from datetime import datetime
from decimal import Decimal, InvalidOperation

from defusedxml import ElementTree as ET

from app.validators.mits.base import BaseValidator, ValidationResult
from app.validators.mits.enums import TermBasis, validate_enum


class SectionIValidator(BaseValidator):
    """
    Validator for Section I: Amount Blocks.

    Rules:
        57. Each amount block must contain at least one of: Amounts or Percentage
        58. <Amounts>: every value is a valid decimal with up to two fractional digits
        59. <Amounts> values must be ≥ 0 (zero allowed when valid per basis rules)
        60. <Percentage>: valid decimal ≥ 0
        61. Percentages > 100 are allowed (e.g., 200% early termination)
        62. <TermBasis> must be "Whole Lease" or "Whole Term" if present
        63. StartTermEarliest and StartTermLatest: if both present, Earliest ≤ Latest
        64. For scheduled pricing, StartTermEarliest required, dates parseable, non-overlapping windows
        65. <Duration> if present must be integer ≥ 0
    """

    section_name = "Amount Blocks"
    section_id = "I"

    VALID_ITEM_TYPES = {
        "ChargeOfferItem",
        "PetOfferItem",
        "ParkingOfferItem",
        "StorageOfferItem",
    }

    def validate(self) -> ValidationResult:
        """
        Execute Section I validation rules.

        Returns:
            ValidationResult with any errors found
        """
        for class_elem in self.root.iter("ChargeOfferClass"):
            class_code = class_elem.get("Code", "unknown")
            items = [child for child in class_elem if child.tag in self.VALID_ITEM_TYPES]

            for item in items:
                item_code = item.get("InternalCode", "unknown")
                self._validate_item_amount_blocks(item, item_code, class_code)

        return self.result

    def _validate_item_amount_blocks(
        self, item: ET.Element, item_code: str, class_code: str
    ) -> None:
        """
        Validate all amount blocks for a single item.

        Args:
            item: Offer item element
            item_code: InternalCode of the item
            class_code: Code of the parent class
        """
        item_path = self.get_element_path(item)
        amount_blocks = item.findall("ChargeOfferAmount")

        scheduled_windows = []  # For Rule I.64.3 - track windows for overlap detection

        for idx, block in enumerate(amount_blocks, start=1):
            block_path = f"{item_path}/ChargeOfferAmount[{idx}]"
            window = self._validate_amount_block(block, item_code, class_code, block_path)
            if window:
                scheduled_windows.append((idx, window))

        # Rule I.64.3: Check for overlapping scheduled windows
        if len(scheduled_windows) > 1:
            self._check_overlapping_windows(scheduled_windows, item_code, class_code, item_path)

    def _validate_amount_block(
        self, block: ET.Element, item_code: str, class_code: str, block_path: str
    ) -> tuple | None:
        """
        Validate a single ChargeOfferAmount block.

        Args:
            block: ChargeOfferAmount element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            block_path: Path to block for error messages

        Returns:
            Tuple of (start_date, end_date) if scheduled pricing is used, None otherwise
        """
        amounts_elem = block.find("Amounts")
        percentage_elem = block.find("Percentage")

        amounts_text = self.get_text(amounts_elem) if amounts_elem is not None else ""
        percentage_text = self.get_text(percentage_elem) if percentage_elem is not None else ""

        # Rule I.57: Must contain at least one of Amounts or Percentage
        if not amounts_text and not percentage_text:
            self.result.add_error(
                rule_id="I.57",
                message=f"Amount block in item '{item_code}' has both empty <Amounts> and <Percentage>. "
                f"At least one must be present",
                element_path=block_path,
                details={"class_code": class_code, "item_code": item_code},
            )

        # Rules I.58 & I.59: Validate Amounts
        if amounts_text:
            self._validate_amounts(amounts_text, item_code, class_code, f"{block_path}/Amounts")

        # Rule I.60 & I.61: Validate Percentage
        if percentage_text:
            self._validate_percentage(percentage_text, item_code, class_code, f"{block_path}/Percentage")

        # Rule I.62: Validate TermBasis
        term_basis_elem = block.find("TermBasis")
        if term_basis_elem is not None:
            term_basis = self.get_text(term_basis_elem)
            if term_basis:
                valid, error_msg = validate_enum(term_basis, TermBasis, "I.62", "TermBasis")
                if not valid:
                    self.result.add_error(
                        rule_id="I.62",
                        message=error_msg,
                        element_path=f"{block_path}/TermBasis",
                        details={"class_code": class_code, "item_code": item_code},
                    )

        # Rules I.63 & I.64: Validate date fields
        return self._validate_dates(block, item_code, class_code, block_path)

    def _validate_amounts(
        self, amounts_text: str, item_code: str, class_code: str, amounts_path: str
    ) -> None:
        """
        Validate Rules I.58 & I.59: Amounts format and values.

        Args:
            amounts_text: Text content of Amounts element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            amounts_path: Path to Amounts for error messages
        """
        # Parse comma/newline-separated values
        amount_values = [
            a.strip()
            for a in amounts_text.replace("\n", ",").replace("\t", ",").split(",")
            if a.strip()
        ]

        for val in amount_values:
            # Rule I.58: Valid decimal with up to two fractional digits
            try:
                decimal_val = Decimal(val)

                # Check fractional digits (up to 2 allowed)
                # Get the exponent to determine decimal places
                exponent = decimal_val.as_tuple().exponent
                if exponent < -2:
                    self.result.add_error(
                        rule_id="I.58",
                        message=f"Amount value '{val}' in item '{item_code}' has more than 2 decimal places",
                        element_path=amounts_path,
                        details={"class_code": class_code, "item_code": item_code, "value": val},
                    )

                # Rule I.59: Values must be ≥ 0
                if decimal_val < 0:
                    self.result.add_error(
                        rule_id="I.59",
                        message=f"Amount value '{val}' in item '{item_code}' must be ≥ 0",
                        element_path=amounts_path,
                        details={"class_code": class_code, "item_code": item_code, "value": val},
                    )

            except (InvalidOperation, ValueError):
                self.result.add_error(
                    rule_id="I.58",
                    message=f"Amount value '{val}' in item '{item_code}' is not a valid decimal number",
                    element_path=amounts_path,
                    details={"class_code": class_code, "item_code": item_code, "value": val},
                )

    def _validate_percentage(
        self, percentage_text: str, item_code: str, class_code: str, percentage_path: str
    ) -> None:
        """
        Validate Rules I.60 & I.61: Percentage format and values.

        Args:
            percentage_text: Text content of Percentage element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            percentage_path: Path to Percentage for error messages
        """
        try:
            percentage_val = Decimal(percentage_text)

            # Rule I.60: Valid decimal ≥ 0
            if percentage_val < 0:
                self.result.add_error(
                    rule_id="I.60",
                    message=f"Percentage value '{percentage_text}' in item '{item_code}' must be ≥ 0",
                    element_path=percentage_path,
                    details={"class_code": class_code, "item_code": item_code, "value": percentage_text},
                )

            # Rule I.61: Percentages > 100 are allowed (just informational note)
            # No error, but could add an info message if useful
            if percentage_val > 100:
                self.result.add_info(
                    rule_id="I.61",
                    message=f"Percentage value {percentage_text}% in item '{item_code}' exceeds 100% "
                    f"(allowed for cases like early termination fees)",
                    element_path=percentage_path,
                    details={"class_code": class_code, "item_code": item_code, "value": percentage_text},
                )

        except (InvalidOperation, ValueError):
            self.result.add_error(
                rule_id="I.60",
                message=f"Percentage value '{percentage_text}' in item '{item_code}' is not a valid decimal number",
                element_path=percentage_path,
                details={"class_code": class_code, "item_code": item_code, "value": percentage_text},
            )

    def _validate_dates(
        self, block: ET.Element, item_code: str, class_code: str, block_path: str
    ) -> tuple | None:
        """
        Validate Rules I.63, I.64, I.65: Date fields and scheduled pricing.

        Args:
            block: ChargeOfferAmount element
            item_code: InternalCode of the item
            class_code: Code of the parent class
            block_path: Path to block for error messages

        Returns:
            Tuple of (start_date, end_date) if valid scheduled pricing, None otherwise
        """
        start_earliest_elem = block.find("StartTermEarliest")
        start_latest_elem = block.find("StartTermLatest")
        duration_elem = block.find("Duration")

        start_earliest = self.get_text(start_earliest_elem) if start_earliest_elem is not None else ""
        start_latest = self.get_text(start_latest_elem) if start_latest_elem is not None else ""
        duration = self.get_text(duration_elem) if duration_elem is not None else ""

        # Rule I.65: Duration must be integer ≥ 0
        if duration:
            try:
                duration_val = int(duration)
                if duration_val < 0:
                    self.result.add_error(
                        rule_id="I.65",
                        message=f"<Duration> in item '{item_code}' must be ≥ 0, found '{duration}'",
                        element_path=f"{block_path}/Duration",
                        details={"class_code": class_code, "item_code": item_code},
                    )
            except ValueError:
                self.result.add_error(
                    rule_id="I.65",
                    message=f"<Duration> in item '{item_code}' must be an integer, found '{duration}'",
                    element_path=f"{block_path}/Duration",
                    details={"class_code": class_code, "item_code": item_code},
                )

        # Check if this is scheduled pricing (any date field present)
        has_date_fields = bool(start_earliest or start_latest)

        if not has_date_fields:
            return None  # Not scheduled pricing

        # Rule I.64.1: If scheduled pricing, StartTermEarliest is required
        if not start_earliest:
            self.result.add_error(
                rule_id="I.64.1",
                message=f"Scheduled pricing in item '{item_code}' missing required <StartTermEarliest>",
                element_path=block_path,
                details={"class_code": class_code, "item_code": item_code},
            )
            return None

        # Rule I.64.2: Dates must be parseable
        earliest_date = self._parse_date(start_earliest, item_code, class_code, f"{block_path}/StartTermEarliest")
        latest_date = None

        if start_latest:
            latest_date = self._parse_date(start_latest, item_code, class_code, f"{block_path}/StartTermLatest")

        if earliest_date is None:
            return None  # Parse error already reported

        # Rule I.63: If both present, Earliest ≤ Latest
        if latest_date and earliest_date > latest_date:
            self.result.add_error(
                rule_id="I.63",
                message=f"StartTermEarliest ({start_earliest}) > StartTermLatest ({start_latest}) in item '{item_code}'",
                element_path=block_path,
                details={"class_code": class_code, "item_code": item_code},
            )

        # Return window for overlap checking
        return (earliest_date, latest_date or earliest_date)

    def _parse_date(
        self, date_str: str, item_code: str, class_code: str, date_path: str
    ) -> datetime | None:
        """
        Parse a date string, trying common formats.

        Args:
            date_str: Date string to parse
            item_code: InternalCode of the item
            class_code: Code of the parent class
            date_path: Path to date field for error messages

        Returns:
            datetime object if parseable, None otherwise
        """
        # Try common date formats
        formats = [
            "%Y-%m-%d",  # ISO format
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%d/%m/%Y",
            "%Y-%m-%dT%H:%M:%S",  # ISO with time
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # Rule I.64.2: Date must be parseable
        self.result.add_error(
            rule_id="I.64.2",
            message=f"Date value '{date_str}' in item '{item_code}' is not in a recognized format",
            element_path=date_path,
            details={"class_code": class_code, "item_code": item_code, "value": date_str},
        )
        return None

    def _check_overlapping_windows(
        self,
        windows: list[tuple[int, tuple]],
        item_code: str,
        class_code: str,
        item_path: str,
    ) -> None:
        """
        Check for overlapping scheduled pricing windows.

        Args:
            windows: List of (block_idx, (start_date, end_date)) tuples
            item_code: InternalCode of the item
            class_code: Code of the parent class
            item_path: Path to item for error messages
        """
        # Rule I.64.3: Multiple scheduled blocks must have non-overlapping windows
        for i in range(len(windows)):
            for j in range(i + 1, len(windows)):
                idx1, (start1, end1) = windows[i]
                idx2, (start2, end2) = windows[j]

                # Check for overlap
                if start1 <= end2 and start2 <= end1:
                    self.result.add_error(
                        rule_id="I.64.3",
                        message=f"Item '{item_code}' has overlapping scheduled pricing windows: "
                        f"block #{idx1} and block #{idx2}",
                        element_path=item_path,
                        details={
                            "class_code": class_code,
                            "item_code": item_code,
                            "block1": idx1,
                            "block2": idx2,
                        },
                    )

