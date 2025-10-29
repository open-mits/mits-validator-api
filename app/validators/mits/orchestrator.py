"""
MITS 5.0 Validator Orchestrator

Coordinates all section validators and returns comprehensive validation results.
"""

import logging
from typing import Dict, List

from defusedxml import ElementTree as ET

from app.validators.mits.base import ValidationResult
from app.validators.mits.xml_structure import XmlStructureValidator, validate_xml_wellformed
from app.validators.mits.fee_hierarchy import FeeHierarchyValidator
from app.validators.mits.identity_uniqueness import IdentityUniquenessValidator
from app.validators.mits.charge_class import ChargeClassValidator
from app.validators.mits.class_limits import ClassLimitsValidator
from app.validators.mits.offer_item_structure import OfferItemStructureValidator
from app.validators.mits.item_characteristics import ItemCharacteristicsValidator
from app.validators.mits.amount_basis import AmountBasisValidator
from app.validators.mits.amount_format import AmountFormatValidator
from app.validators.mits.frequency_alignment import FrequencyAlignmentValidator
from app.validators.mits.pet_validation import PetValidation
from app.validators.mits.parking_validation import ParkingValidation
from app.validators.mits.storage_validation import StorageValidation
from app.validators.mits.cross_validation import CrossValidation
from app.validators.mits.data_quality import DataQualityValidator

logger = logging.getLogger(__name__)


def validate_mits_document(xml_text: str) -> Dict[str, List[str] | bool]:
    """
    Validate a MITS 5.0 XML document against all specification rules.

    This is the main entry point for MITS 5.0 validation. It orchestrates all
    section validators in the correct order, following the execution strategy
    defined in the specification.

    Execution Order:
        Phase 1: XML well-formedness (short-circuit on failure)
        Phase 2: XML structure, fee hierarchy, identity (short-circuit on failure)
        Phase 3: Class structure & limits
        Phase 4: Items, characteristics, basis, and amount blocks
        Phase 5: Frequency alignment and specialized items (pet/parking/storage)
        Phase 6: Cross-validation, references, and included items
        Phase 7: Data quality, hygiene, dates, and duplicates

    Args:
        xml_text: Raw XML text to validate

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "errors": ["Error message 1", ...],
            "warnings": ["Warning 1", ...],
            "info": ["Info 1", ...]
        }
    """
    logger.info("Starting MITS 5.0 document validation")
    result = ValidationResult(valid=True)

    # Phase 1: XML Well-formedness (Rules A.1-2)
    # Must succeed before we can parse the document
    wellformed_result = validate_xml_wellformed(xml_text)
    result.merge(wellformed_result)

    if not wellformed_result.valid:
        logger.warning("XML well-formedness validation failed, stopping")
        return result.to_dict()

    # Parse the document
    try:
        root = ET.fromstring(xml_text.encode("utf-8"))
    except Exception as e:
        result.add_error(
            rule_id="xml_wellformed",
            message=f"Failed to parse XML: {str(e)}",
        )
        return result.to_dict()

    # Phase 2: Sections A-C - Container, placement, identity (short-circuit on failure)
    logger.info("Validating Sections A-C: Container & Identity")

    section_a = XmlStructureValidator(root)
    result.merge(section_a.validate())

    if not result.valid:
        logger.warning("Critical validation errors in Sections A-C, stopping")
        return result.to_dict()

    section_b = FeeHierarchyValidator(root)
    result.merge(section_b.validate())

    section_c = IdentityUniquenessValidator(root)
    result.merge(section_c.validate())

    # Phase 3: Sections D-E - Class structure & limits
    logger.info("Validating Sections D-E: Class Structure")

    section_d = ChargeClassValidator(root)
    result.merge(section_d.validate())

    section_e = ClassLimitsValidator(root)
    result.merge(section_e.validate())

    # Phase 4: Sections F-I - Items, characteristics, basis, amounts
    logger.info("Validating Sections F-I: Items & Amounts")

    section_f = OfferItemStructureValidator(root)
    result.merge(section_f.validate())

    section_g = ItemCharacteristicsValidator(root)
    result.merge(section_g.validate())

    section_h = AmountBasisValidator(root)
    result.merge(section_h.validate())

    section_i = AmountFormatValidator(root)
    result.merge(section_i.validate())

    # Phase 5: Sections J-M - Per-type semantics & specialized items
    logger.info("Validating Sections J-M: Frequency & Specialized Items")

    section_j = FrequencyAlignmentValidator(root)
    result.merge(section_j.validate())

    section_k = PetValidation(root)
    result.merge(section_k.validate())

    section_l = ParkingValidation(root)
    result.merge(section_l.validate())

    section_m = StorageValidation(root)
    result.merge(section_m.validate())

    # Phase 6: Sections N-P - Cross-field integrity & references
    logger.info("Validating Sections N-P: Integrity & References")

    section_nop = CrossValidation(root)
    result.merge(section_nop.validate())

    # Phase 7: Sections Q-T - Hygiene, dates, coherence, duplicates
    logger.info("Validating Sections Q-T: Hygiene & Duplicates")

    section_qrst = DataQualityValidator(root)
    result.merge(section_qrst.validate())

    # Log summary
    error_count = len(result.errors)
    warning_count = len(result.warnings)
    info_count = len(result.info)

    logger.info(
        f"MITS 5.0 validation complete: valid={result.valid}, "
        f"errors={error_count}, warnings={warning_count}, info={info_count}"
    )

    return result.to_dict()

