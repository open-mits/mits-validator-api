# MITS Validator Naming Convention

This document maps the old section-based naming to new descriptive names.

## Validator Modules

| Old Name | New Name | Purpose |
|----------|----------|---------|
| section_a_xml_basics | xml_structure | XML well-formedness, root element, Property presence |
| section_b_fee_placement | fee_hierarchy | Fee placement in correct parent contexts |
| section_c_identity | identity_uniqueness | Building, Floorplan, Unit ID uniqueness |
| section_d_class_structure | charge_class | ChargeOfferClass structure and codes |
| section_e_class_limits | class_limits | Class occurrence and amount limits |
| section_f_offer_items | offer_item_structure | Item InternalCode, Name, Description, occurrences |
| section_g_characteristics | item_characteristics | ChargeRequirement, Lifecycle, Refundability |
| section_h_amount_basis | amount_basis | Explicit, Percentage Of, Stepped, Variable, Included |
| section_i_amount_blocks | amount_format | Numeric formats, dates, scheduled pricing |
| section_j_frequency | frequency_alignment | AmountPerType and PaymentFrequency coherence |
| section_k_pet_items | pet_validation | PetOfferItem specific rules |
| section_l_parking_items | parking_validation | ParkingOfferItem specific rules |
| section_m_storage_items | storage_validation | StorageOfferItem specific rules |
| section_n_o_p_integrity | cross_validation | References, circular dependencies, included items |
| section_q_r_s_t_final | data_quality | Text hygiene, dates, duplicates |

## Rule ID Mapping

### XML Structure (formerly Section A)
- A.1 → xml_wellformed
- A.2 → xml_encoding_utf8
- A.3 → root_is_physical_property
- A.4 → property_exists
- A.5 → property_has_id
- A.6 → property_id_unique

### Fee Hierarchy (formerly Section B)
- B.7 → fee_in_valid_parent
- B.8 → fee_uses_class_container
- B.9 → class_item_amount_structure
- B.10 → no_fee_outside_hierarchy

### Identity Uniqueness (formerly Section C)
- C.11 → building_id_unique
- C.12 → floorplan_id_unique
- C.13 → unit_id_unique
- C.14 → id_no_whitespace

### Charge Class (formerly Section D)
- D.15 → class_has_code
- D.16 → class_code_across_parents
- D.17 → class_code_unique_in_parent
- D.18 → class_has_items
- D.19 → class_no_empty_children
- D.20 → class_limits_optional

### Class Limits (formerly Section E)
- E.21 → limit_max_occurrences_valid
- E.22 → limit_max_amount_valid
- E.23 → limit_applies_to_structure
- E.24 → limit_internal_code_nonempty
- E.25 → limit_characteristics_valid
- E.26 → limit_both_optional

### Offer Item Structure (formerly Section F)
- F.27 → item_has_internal_code
- F.28 → item_internal_code_unique
- F.29 → item_no_duplicate_semantics
- F.30 → item_has_name
- F.31 → item_has_description
- F.32 → item_has_one_characteristics
- F.33 → item_has_amount_blocks
- F.34 → item_min_occurrence_valid
- F.35 → item_max_occurrence_valid
- F.36 → item_occurrence_range_valid
- F.37 → item_amount_basis_required
- F.38 → item_percentage_code_when_needed
- F.39 → item_amount_per_type_valid
- F.40 → item_pms_fields_optional
- F.41 → ~~item_no_unexpected_children~~ (REMOVED - unknown child elements now allowed)

### Item Characteristics (formerly Section G)
- G.42 → char_requirement_required
- G.43 → char_conditional_scope_valid
- G.43.1 → char_conditional_has_codes
- G.43.2 → char_conditional_code_exists
- G.43.3 → char_no_self_reference
- G.43.4 → char_no_circular_reference
- G.44 → char_lifecycle_required
- G.45 → char_frequency_valid
- G.46 → char_refundability_valid
- G.47 → char_refund_details_required
- G.47.1 → char_refund_max_type_required
- G.47.2 → char_refund_max_required
- G.48 → char_refund_per_type_valid
- G.49 → char_requirement_desc_nonempty

### Amount Basis (formerly Section H)
- H.50 → basis_enum_valid
- H.51 → basis_explicit_has_amounts
- H.51.1 → basis_explicit_amounts_nonempty
- H.51.2 → basis_explicit_percentage_empty
- H.52 → basis_percentage_structure
- H.52.1 → basis_percentage_has_value
- H.52.2 → basis_percentage_amounts_empty
- H.52.3 → basis_percentage_has_code
- H.52.4 → basis_percentage_no_circular
- H.53 → basis_range_one_amount
- H.53.1 → basis_range_single_value
- H.54 → basis_stepped_multiple_amounts
- H.54.1 → basis_stepped_min_two
- H.54.2 → basis_stepped_order_valid
- H.54.3 → basis_stepped_zero_allowed
- H.55 → basis_variable_either_or
- H.55.1 → basis_variable_not_both
- H.56 → basis_included_empty
- H.56.1 → basis_included_no_basis
- H.56.2 → basis_included_amounts_empty
- H.56.3 → basis_included_percentage_empty

### Amount Format (formerly Section I)
- I.57 → amount_has_value
- I.58 → amount_decimal_format
- I.59 → amount_non_negative
- I.60 → percentage_decimal_valid
- I.61 → percentage_over_100_allowed
- I.62 → term_basis_valid
- I.63 → date_range_valid
- I.64 → scheduled_pricing_valid
- I.64.1 → scheduled_has_start_date
- I.64.2 → scheduled_date_parseable
- I.64.3 → scheduled_no_overlap
- I.65 → duration_integer_valid

### Frequency Alignment (formerly Section J)
- J.66 → amount_per_type_enum
- J.67 → amount_per_applicant_note
- J.68 → frequency_basis_coherent
- J.69 → onetime_with_term_basis

### Pet Validation (formerly Section K)
- K.70 → pet_optional_fields
- K.71 → pet_allowed_enum
- K.72 → pet_not_allowed_no_amount
- K.73 → pet_weight_format
- K.74 → pet_deposit_refund_required

### Parking Validation (formerly Section L)
- L.75 → parking_optional_fields
- L.76 → parking_included_semantics
- L.77 → parking_electric_enum
- L.78 → parking_space_enum

### Storage Validation (formerly Section M)
- M.79 → storage_optional_fields
- M.80 → storage_dimensions_valid
- M.81 → storage_unit_recognized

### Cross Validation (formerly Section N-O-P)
- N.82 → internal_code_unique_in_class
- N.83 → class_code_unique_in_parent
- N.84 → cross_level_isolation
- N.85 → limit_applies_to_same_class
- N.86 → limit_occurrence_cap_runtime
- N.87 → limit_amount_cap_runtime
- N.88 → limit_characteristics_filter
- N.89 → limit_all_items_no_filter
- O.90 → reference_code_exists
- O.91 → reference_no_self
- O.92 → reference_no_circular
- O.93 → reference_not_included
- O.94 → reference_no_overlap
- P.95 → included_no_amounts
- P.96 → included_no_recurring
- P.97 → included_dates_allowed

### Data Quality (formerly Section Q-R-S-T)
- Q.98 → text_required_nonempty
- Q.99 → numeric_no_symbols
- Q.100 → numeric_no_plus_sign
- Q.101 → text_no_control_chars
- Q.102 → text_normalize_crlf
- R.103 → date_format_valid
- R.104 → date_no_overlap_in_item
- R.105 → date_overlap_warning
- S.106 → frequency_not_with_period
- S.107 → frequency_range_warning
- S.108 → during_term_needs_frequency
- T.109 → name_unique_in_class
- T.110 → no_duplicate_items

## File Structure

```
app/validators/mits/
├── __init__.py
├── base.py
├── enums.py
├── orchestrator.py
├── xml_structure.py              # Rules: xml_*
├── fee_hierarchy.py              # Rules: fee_*
├── identity_uniqueness.py        # Rules: building_*, floorplan_*, unit_*, id_*
├── charge_class.py               # Rules: class_*
├── class_limits.py               # Rules: limit_*
├── offer_item_structure.py       # Rules: item_*
├── item_characteristics.py       # Rules: char_*
├── amount_basis.py               # Rules: basis_*
├── amount_format.py              # Rules: amount_*, percentage_*, term_*, date_*, scheduled_*, duration_*
├── frequency_alignment.py        # Rules: frequency_*, amount_per_*, onetime_*
├── pet_validation.py             # Rules: pet_*
├── parking_validation.py         # Rules: parking_*
├── storage_validation.py         # Rules: storage_*
├── cross_validation.py           # Rules: reference_*, internal_code_*, class_code_*, included_*
└── data_quality.py               # Rules: text_*, numeric_*, date_*, name_*, no_duplicate_*
```

## Class Names

| Old Class | New Class |
|-----------|-----------|
| SectionAValidator | XmlStructureValidator |
| SectionBValidator | FeeHierarchyValidator |
| SectionCValidator | IdentityUniquenessValidator |
| SectionDValidator | ChargeClassValidator |
| SectionEValidator | ClassLimitsValidator |
| SectionFValidator | OfferItemStructureValidator |
| SectionGValidator | ItemCharacteristicsValidator |
| SectionHValidator | AmountBasisValidator |
| SectionIValidator | AmountFormatValidator |
| SectionJValidator | FrequencyAlignmentValidator |
| SectionKValidator | PetValidation |
| SectionLValidator | ParkingValidation |
| SectionMValidator | StorageValidation |
| SectionNOPValidator | CrossValidation |
| SectionQRSTValidator | DataQualityValidator |

## Benefits

1. **Self-documenting**: Names clearly indicate what is being validated
2. **Grep-friendly**: Easy to find all rules related to "item" or "amount"
3. **Maintainable**: Adding new rules doesn't require renumbering
4. **Scalable**: New validators can be added with clear naming patterns
5. **Error messages**: Users see descriptive rule names instead of cryptic codes

## Migration Strategy

1. Rename files
2. Update class names
3. Update rule IDs in all validators
4. Update tests
5. Update orchestrator
6. Update documentation
7. Keep backward compatibility mapping if needed

