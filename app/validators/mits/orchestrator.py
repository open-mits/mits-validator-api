"""
MITS 5.0 Validator Orchestrator

Coordinates all section validators and returns comprehensive validation results.
"""

import logging
from typing import Dict, List

from defusedxml import ElementTree as ET

from app.validators.mits.base import ValidationResult
from app.validators.mits.section_a_xml_basics import SectionAValidator, validate_xml_wellformed
from app.validators.mits.section_b_fee_placement import SectionBValidator
from app.validators.mits.section_c_identity import SectionCValidator
from app.validators.mits.section_d_class_structure import SectionDValidator
from app.validators.mits.section_e_class_limits import SectionEValidator
from app.validators.mits.section_f_offer_items import SectionFValidator
from app.validators.mits.section_g_characteristics import SectionGValidator
from app.validators.mits.section_h_amount_basis import SectionHValidator
from app.validators.mits.section_i_amount_blocks import SectionIValidator
from app.validators.mits.section_j_frequency import SectionJValidator
from app.validators.mits.section_k_pet_items import SectionKValidator
from app.validators.mits.section_l_parking_items import SectionLValidator
from app.validators.mits.section_m_storage_items import SectionMValidator
from app.validators.mits.section_n_o_p_integrity import SectionNOPValidator
from app.validators.mits.section_q_r_s_t_final import SectionQRSTValidator

logger = logging.getLogger(__name__)


def validate_mits_document(xml_text: str) -> Dict[str, List[str] | bool]:
    """
    Validate a MITS 5.0 XML document against all specification rules.

    This is the main entry point for MITS 5.0 validation. It orchestrates all
    section validators in the correct order, following the execution strategy
    defined in the specification.

    Execution Order:
        A-C: Container, placement, and identity (short-circuit on failure)
        D-E: Class existence & limits
        F-I: Items, characteristics, basis, and amount blocks
        J-M: Per-type semantics and specialized items
        N-P: Cross-field totals, references, and Included semantics
        Q-T: Hygiene, dates, cadence/basis coherence, and duplicates

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
            rule_id="A.1",
            message=f"Failed to parse XML: {str(e)}",
        )
        return result.to_dict()

    # Phase 2: Sections A-C - Container, placement, identity (short-circuit on failure)
    logger.info("Validating Sections A-C: Container & Identity")

    section_a = SectionAValidator(root)
    result.merge(section_a.validate())

    if not result.valid:
        logger.warning("Critical validation errors in Sections A-C, stopping")
        return result.to_dict()

    section_b = SectionBValidator(root)
    result.merge(section_b.validate())

    section_c = SectionCValidator(root)
    result.merge(section_c.validate())

    # Phase 3: Sections D-E - Class structure & limits
    logger.info("Validating Sections D-E: Class Structure")

    section_d = SectionDValidator(root)
    result.merge(section_d.validate())

    section_e = SectionEValidator(root)
    result.merge(section_e.validate())

    # Phase 4: Sections F-I - Items, characteristics, basis, amounts
    logger.info("Validating Sections F-I: Items & Amounts")

    section_f = SectionFValidator(root)
    result.merge(section_f.validate())

    section_g = SectionGValidator(root)
    result.merge(section_g.validate())

    section_h = SectionHValidator(root)
    result.merge(section_h.validate())

    section_i = SectionIValidator(root)
    result.merge(section_i.validate())

    # Phase 5: Sections J-M - Per-type semantics & specialized items
    logger.info("Validating Sections J-M: Frequency & Specialized Items")

    section_j = SectionJValidator(root)
    result.merge(section_j.validate())

    section_k = SectionKValidator(root)
    result.merge(section_k.validate())

    section_l = SectionLValidator(root)
    result.merge(section_l.validate())

    section_m = SectionMValidator(root)
    result.merge(section_m.validate())

    # Phase 6: Sections N-P - Cross-field integrity & references
    logger.info("Validating Sections N-P: Integrity & References")

    section_nop = SectionNOPValidator(root)
    result.merge(section_nop.validate())

    # Phase 7: Sections Q-T - Hygiene, dates, coherence, duplicates
    logger.info("Validating Sections Q-T: Hygiene & Duplicates")

    section_qrst = SectionQRSTValidator(root)
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

