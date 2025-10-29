"""
Base classes and models for MITS 5.0 validators.

Provides common validation result structures and base validator classes.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Optional

from defusedxml import ElementTree as ET


class ValidationSeverity(Enum):
    """Severity levels for validation messages."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationMessage:
    """A single validation message."""

    rule_id: str  # e.g., "A.1", "B.7"
    severity: ValidationSeverity
    message: str
    element_path: Optional[str] = None  # XPath-like location
    details: Optional[dict] = None

    def __str__(self) -> str:
        """Format message for display."""
        location = f" at {self.element_path}" if self.element_path else ""
        return f"[{self.rule_id}] {self.message}{location}"


@dataclass
class ValidationResult:
    """Result of a validation operation."""

    valid: bool
    errors: List[ValidationMessage] = field(default_factory=list)
    warnings: List[ValidationMessage] = field(default_factory=list)
    info: List[ValidationMessage] = field(default_factory=list)

    def add_error(
        self,
        rule_id: str,
        message: str,
        element_path: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Add an error message."""
        self.errors.append(
            ValidationMessage(
                rule_id=rule_id,
                severity=ValidationSeverity.ERROR,
                message=message,
                element_path=element_path,
                details=details,
            )
        )
        self.valid = False

    def add_warning(
        self,
        rule_id: str,
        message: str,
        element_path: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Add a warning message."""
        self.warnings.append(
            ValidationMessage(
                rule_id=rule_id,
                severity=ValidationSeverity.WARNING,
                message=message,
                element_path=element_path,
                details=details,
            )
        )

    def add_info(
        self,
        rule_id: str,
        message: str,
        element_path: Optional[str] = None,
        details: Optional[dict] = None,
    ) -> None:
        """Add an informational message."""
        self.info.append(
            ValidationMessage(
                rule_id=rule_id,
                severity=ValidationSeverity.INFO,
                message=message,
                element_path=element_path,
                details=details,
            )
        )

    def merge(self, other: "ValidationResult") -> None:
        """Merge another result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.info.extend(other.info)
        if not other.valid:
            self.valid = False

    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {
            "valid": self.valid,
            "errors": [str(e) for e in self.errors],
            "warnings": [str(w) for w in self.warnings],
            "info": [str(i) for i in self.info],
        }


class BaseValidator:
    """Base class for MITS validators."""

    section_name: str = "Base"
    section_id: str = "X"

    def __init__(self, root: ET.Element):
        """
        Initialize validator with parsed XML root.

        Args:
            root: Root element of the parsed XML document
        """
        self.root = root
        self.result = ValidationResult(valid=True)

    def validate(self) -> ValidationResult:
        """
        Run validation checks.

        Returns:
            ValidationResult with errors, warnings, and info messages
        """
        raise NotImplementedError("Subclasses must implement validate()")

    def get_element_path(self, element: ET.Element) -> str:
        """
        Get a human-readable path for an element.

        Args:
            element: XML element

        Returns:
            String representation of element's location
        """
        # Build path by traversing up the tree
        path_parts = []
        current = element

        # Walk up to find position in tree
        while current is not None:
            tag = current.tag
            # Try to add identifying attribute if available
            id_val = current.get("IDValue") or current.get("InternalCode") or current.get("Code")
            if id_val:
                tag = f"{tag}[@id='{id_val}']"
            path_parts.insert(0, tag)

            # Move to parent (this is simplified - in real XML tree walking you'd use parent map)
            break  # For now, just show immediate element

        return "/" + "/".join(path_parts)

    def get_text(self, element: ET.Element, default: str = "") -> str:
        """
        Safely get text content from element.

        Args:
            element: XML element
            default: Default value if text is None

        Returns:
            Text content or default
        """
        return (element.text or default).strip()

    def is_empty_text(self, text: Optional[str]) -> bool:
        """
        Check if text is empty or whitespace only.

        Args:
            text: Text to check

        Returns:
            True if empty or whitespace only
        """
        return not text or not text.strip()

