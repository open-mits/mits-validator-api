#!/usr/bin/env python3
"""
Script to rename all validator classes and rule IDs to descriptive names.
"""

import re
from pathlib import Path

# Mapping of old to new names
CLASS_MAPPING = {
    "SectionAValidator": "XmlStructureValidator",
    "SectionBValidator": "FeeHierarchyValidator",
    "SectionCValidator": "IdentityUniquenessValidator",
    "SectionDValidator": "ChargeClassValidator",
    "SectionEValidator": "ClassLimitsValidator",
    "SectionFValidator": "OfferItemStructureValidator",
    "SectionGValidator": "ItemCharacteristicsValidator",
    "SectionHValidator": "AmountBasisValidator",
    "SectionIValidator": "AmountFormatValidator",
    "SectionJValidator": "FrequencyAlignmentValidator",
    "SectionKValidator": "PetValidation",
    "SectionLValidator": "ParkingValidation",
    "SectionMValidator": "StorageValidation",
    "SectionNOPValidator": "CrossValidation",
    "SectionQRSTValidator": "DataQualityValidator",
}

SECTION_ID_MAPPING = {
    '"A"': '"xml_structure"',
    '"B"': '"fee_hierarchy"',
    '"C"': '"identity_uniqueness"',
    '"D"': '"charge_class"',
    '"E"': '"class_limits"',
    '"F"': '"offer_item_structure"',
    '"G"': '"item_characteristics"',
    '"H"': '"amount_basis"',
    '"I"': '"amount_format"',
    '"J"': '"frequency_alignment"',
    '"K"': '"pet_validation"',
    '"L"': '"parking_validation"',
    '"M"': '"storage_validation"',
    '"N-O-P"': '"cross_validation"',
    '"Q-R-S-T"': '"data_quality"',
}

# Rule ID mapping - comprehensive list
RULE_MAPPING = {
    # Section A -> XML Structure
    '"A.1"': '"xml_wellformed"',
    '"A.2"': '"xml_encoding_utf8"',
    '"A.3"': '"root_is_physical_property"',
    '"A.4"': '"property_exists"',
    '"A.5"': '"property_has_id"',
    '"A.6"': '"property_id_unique"',
    
    # Section B -> Fee Hierarchy
    '"B.7"': '"fee_in_valid_parent"',
    '"B.8"': '"fee_uses_class_container"',
    '"B.9"': '"class_item_amount_structure"',
    '"B.10"': '"no_fee_outside_hierarchy"',
    
    # Section C -> Identity Uniqueness
    '"C.11"': '"building_id_unique"',
    '"C.12"': '"floorplan_id_unique"',
    '"C.13"': '"unit_id_unique"',
    '"C.14"': '"id_no_whitespace"',
    
    # Section D -> Charge Class
    '"D.15"': '"class_has_code"',
    '"D.16"': '"class_code_across_parents"',
    '"D.17"': '"class_code_unique_in_parent"',
    '"D.18"': '"class_has_items"',
    '"D.19"': '"class_no_empty_children"',
    '"D.20"': '"class_limits_optional"',
    
    # Section E -> Class Limits
    '"E.21"': '"limit_max_occurrences_valid"',
    '"E.22"': '"limit_max_amount_valid"',
    '"E.23"': '"limit_applies_to_structure"',
    '"E.24"': '"limit_internal_code_nonempty"',
    '"E.25"': '"limit_characteristics_valid"',
    '"E.26"': '"limit_both_optional"',
    
    # Section F -> Offer Item Structure
    '"F.27"': '"item_has_internal_code"',
    '"F.28"': '"item_internal_code_unique"',
    '"F.29"': '"item_no_duplicate_semantics"',
    '"F.30"': '"item_has_name"',
    '"F.31"': '"item_has_description"',
    '"F.32"': '"item_has_one_characteristics"',
    '"F.33"': '"item_has_amount_blocks"',
    '"F.34"': '"item_min_occurrence_valid"',
    '"F.35"': '"item_max_occurrence_valid"',
    '"F.36"': '"item_occurrence_range_valid"',
    '"F.37"': '"item_amount_basis_required"',
    '"F.38"': '"item_percentage_code_when_needed"',
    '"F.39"': '"item_amount_per_type_valid"',
    '"F.40"': '"item_pms_fields_optional"',
    '"F.41"': '"item_no_unexpected_children"',
    
    # Section G -> Item Characteristics
    '"G.42"': '"char_requirement_required"',
    '"G.43"': '"char_conditional_scope_valid"',
    '"G.43.1"': '"char_conditional_has_codes"',
    '"G.43.2"': '"char_conditional_code_exists"',
    '"G.43.3"': '"char_no_self_reference"',
    '"G.43.4"': '"char_no_circular_reference"',
    '"G.44"': '"char_lifecycle_required"',
    '"G.45"': '"char_frequency_valid"',
    '"G.46"': '"char_refundability_valid"',
    '"G.47"': '"char_refund_details_required"',
    '"G.47.1"': '"char_refund_max_type_required"',
    '"G.47.2"': '"char_refund_max_required"',
    '"G.48"': '"char_refund_per_type_valid"',
    '"G.49"': '"char_requirement_desc_nonempty"',
    
    # Section H -> Amount Basis
    '"H.50"': '"basis_enum_valid"',
    '"H.51"': '"basis_explicit_has_amounts"',
    '"H.51.1"': '"basis_explicit_amounts_nonempty"',
    '"H.51.2"': '"basis_explicit_percentage_empty"',
    '"H.52"': '"basis_percentage_structure"',
    '"H.52.1"': '"basis_percentage_has_value"',
    '"H.52.2"': '"basis_percentage_amounts_empty"',
    '"H.52.3"': '"basis_percentage_has_code"',
    '"H.52.4"': '"basis_percentage_no_circular"',
    '"H.53"': '"basis_range_one_amount"',
    '"H.53.1"': '"basis_range_single_value"',
    '"H.54"': '"basis_stepped_multiple_amounts"',
    '"H.54.1"': '"basis_stepped_min_two"',
    '"H.54.2"': '"basis_stepped_order_valid"',
    '"H.54.3"': '"basis_stepped_zero_allowed"',
    '"H.55"': '"basis_variable_either_or"',
    '"H.55.1"': '"basis_variable_not_both"',
    '"H.56"': '"basis_included_empty"',
    '"H.56.1"': '"basis_included_no_basis"',
    '"H.56.2"': '"basis_included_amounts_empty"',
    '"H.56.3"': '"basis_included_percentage_empty"',
    
    # Section I -> Amount Format
    '"I.57"': '"amount_has_value"',
    '"I.58"': '"amount_decimal_format"',
    '"I.59"': '"amount_non_negative"',
    '"I.60"': '"percentage_decimal_valid"',
    '"I.61"': '"percentage_over_100_allowed"',
    '"I.62"': '"term_basis_valid"',
    '"I.63"': '"date_range_valid"',
    '"I.64"': '"scheduled_pricing_valid"',
    '"I.64.1"': '"scheduled_has_start_date"',
    '"I.64.2"': '"scheduled_date_parseable"',
    '"I.64.3"': '"scheduled_no_overlap"',
    '"I.65"': '"duration_integer_valid"',
    
    # Section J -> Frequency Alignment
    '"J.66"': '"amount_per_type_enum"',
    '"J.67"': '"amount_per_applicant_note"',
    '"J.68"': '"frequency_basis_coherent"',
    '"J.69"': '"onetime_with_term_basis"',
    
    # Section K -> Pet Validation
    '"K.70"': '"pet_optional_fields"',
    '"K.71"': '"pet_allowed_enum"',
    '"K.72"': '"pet_not_allowed_no_amount"',
    '"K.73"': '"pet_weight_format"',
    '"K.74"': '"pet_deposit_refund_required"',
    
    # Section L -> Parking Validation
    '"L.75"': '"parking_optional_fields"',
    '"L.76"': '"parking_included_semantics"',
    '"L.77"': '"parking_electric_enum"',
    '"L.78"': '"parking_space_enum"',
    
    # Section M -> Storage Validation
    '"M.79"': '"storage_optional_fields"',
    '"M.80"': '"storage_dimensions_valid"',
    '"M.81"': '"storage_unit_recognized"',
    
    # Section N-P -> Cross Validation
    '"N.82"': '"internal_code_unique_in_class"',
    '"N.83"': '"class_code_unique_in_parent"',
    '"N.84"': '"cross_level_isolation"',
    '"N.85"': '"limit_applies_to_same_class"',
    '"N.86"': '"limit_occurrence_cap_runtime"',
    '"N.87"': '"limit_amount_cap_runtime"',
    '"N.88"': '"limit_characteristics_filter"',
    '"N.89"': '"limit_all_items_no_filter"',
    '"O.90"': '"reference_code_exists"',
    '"O.91"': '"reference_no_self"',
    '"O.92"': '"reference_no_circular"',
    '"O.93"': '"reference_not_included"',
    '"O.94"': '"reference_no_overlap"',
    '"P.95"': '"included_no_amounts"',
    '"P.96"': '"included_no_recurring"',
    '"P.97"': '"included_dates_allowed"',
    
    # Section Q-T -> Data Quality
    '"Q.98"': '"text_required_nonempty"',
    '"Q.99"': '"numeric_no_symbols"',
    '"Q.100"': '"numeric_no_plus_sign"',
    '"Q.101"': '"text_no_control_chars"',
    '"Q.102"': '"text_normalize_crlf"',
    '"R.103"': '"date_format_valid"',
    '"R.104"': '"date_no_overlap_in_item"',
    '"R.105"': '"date_overlap_warning"',
    '"S.106"': '"frequency_not_with_period"',
    '"S.107"': '"frequency_range_warning"',
    '"S.108"': '"during_term_needs_frequency"',
    '"T.109"': '"name_unique_in_class"',
    '"T.110"': '"no_duplicate_items"',
}


def replace_in_file(file_path: Path, replacements: dict[str, str]) -> int:
    """Replace strings in a file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return 1
        return 0
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to rename validators."""
    base_path = Path(__file__).parent.parent
    validators_path = base_path / "app" / "validators" / "mits"
    tests_path = base_path / "tests" / "validators" / "mits"
    
    # Combine all replacements
    all_replacements = {}
    all_replacements.update(CLASS_MAPPING)
    all_replacements.update(SECTION_ID_MAPPING)
    all_replacements.update(RULE_MAPPING)
    
    files_updated = 0
    
    # Update validator files
    for py_file in validators_path.glob("*.py"):
        if py_file.name != "__init__.py":
            result = replace_in_file(py_file, all_replacements)
            if result:
                files_updated += result
                print(f"Updated: {py_file.name}")
    
    # Update test files
    for py_file in tests_path.glob("*.py"):
        result = replace_in_file(py_file, all_replacements)
        if result:
            files_updated += result
            print(f"Updated: {py_file.name}")
    
    # Update orchestrator specifically
    orchestrator_file = validators_path / "orchestrator.py"
    if orchestrator_file.exists():
        result = replace_in_file(orchestrator_file, all_replacements)
        if result:
            print(f"Updated: orchestrator.py")
    
    print(f"\nTotal files updated: {files_updated}")


if __name__ == "__main__":
    main()

