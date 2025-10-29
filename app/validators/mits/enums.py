"""
Enumerations for MITS 5.0 validation.

Contains all valid enumerated values referenced in the specification.
"""

from enum import Enum


class ChargeRequirement(Enum):
    """Valid ChargeRequirement values (Rule 42)."""

    INCLUDED = "Included"
    MANDATORY = "Mandatory"
    OPTIONAL = "Optional"
    SITUATIONAL = "Situational"
    CONDITIONAL = "Conditional"


class Lifecycle(Enum):
    """Valid Lifecycle values (Rule 44)."""

    AT_APPLICATION = "At Application"
    MOVE_IN = "Move-in"
    DURING_TERM = "During Term"
    MOVE_OUT = "Move-out"


class PaymentFrequency(Enum):
    """Valid PaymentFrequency values (Rule 45)."""

    ONE_TIME = "One-time"
    MONTHLY = "Monthly"
    QUARTERLY = "Quarterly"
    ANNUALLY = "Annually"
    HOURLY = "Hourly"
    PER_OCCURRENCE = "Per-occurrence"


class Refundability(Enum):
    """Valid Refundability values (Rule 46)."""

    NON_REFUNDABLE = "Non-refundable"
    REFUNDABLE = "Refundable"
    DEPOSIT = "Deposit"


class RefundabilityMaxType(Enum):
    """Valid RefundabilityMaxType values (Rule 47.1)."""

    AMOUNT = "Amount"
    PERCENTAGE = "Percentage"


class AmountBasis(Enum):
    """Valid AmountBasis values (Rule 50)."""

    EXPLICIT = "Explicit"
    PERCENTAGE_OF = "Percentage Of"
    WITHIN_RANGE = "Within Range"
    STEPPED = "Stepped"
    VARIABLE = "Variable"


class TermBasis(Enum):
    """Valid TermBasis values (Rule 62)."""

    WHOLE_LEASE = "Whole Lease"
    WHOLE_TERM = "Whole Term"


class AmountPerType(Enum):
    """Valid AmountPerType values (Rule 66)."""

    ITEM = "Item"
    APPLICANT = "Applicant"
    LEASEHOLDER = "Leaseholder"
    PERSON = "Person"
    PERIOD = "Period"


class PetAllowed(Enum):
    """Valid Allowed values for PetOfferItem (Rule 71)."""

    YES = "Yes"
    NO = "No"


class ParkingElectric(Enum):
    """Valid Electric values for ParkingOfferItem (Rule 77)."""

    NONE = "None"
    AVAILABLE = "Available"


class ParkingSpaceType(Enum):
    """Valid space type values for ParkingOfferItem (Rule 78)."""

    AVAILABLE = "Available"
    NONE = "None"


# Helper functions for validation


def validate_enum(value: str, enum_class: type[Enum], rule_id: str, field_name: str) -> tuple[bool, str]:
    """
    Validate that a value matches one of the allowed enum values.

    Args:
        value: The value to validate
        enum_class: The enum class to validate against
        rule_id: Rule identifier for error messages
        field_name: Name of the field being validated

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not value:
        return True, ""  # Empty is handled by required field checks

    try:
        enum_class(value)
        return True, ""
    except ValueError:
        allowed = ", ".join([e.value for e in enum_class])
        return (
            False,
            f"[{rule_id}] Invalid {field_name} value '{value}'. Allowed values: {allowed}",
        )

