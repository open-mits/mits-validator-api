# MITS Validator Test Plan

## Overview

Comprehensive unit test suite for all 110+ validation rules across 15 validator modules.

## Test Coverage Goals

- **Target Coverage**: ≥90% line and branch coverage
- **Test Types**: Unit tests for each rule with positive and negative cases
- **Test Organization**: One test file per validator module

## Test Files Status

| Test File | Validator | Rules | Test Cases | Status |
|-----------|-----------|-------|------------|--------|
| `test_xml_structure.py` | XmlStructureValidator | 6 | 30+ | ✅ Complete |
| `test_fee_hierarchy.py` | FeeHierarchyValidator | 4 | 15+ | ✅ Complete |
| `test_identity_uniqueness.py` | IdentityUniquenessValidator | 4 | 15+ | ✅ Complete |
| `test_charge_class.py` | ChargeClassValidator | 6 | 20+ | 📝 TODO |
| `test_class_limits.py` | ClassLimitsValidator | 6 | 20+ | 📝 TODO |
| `test_offer_item_structure.py` | OfferItemStructureValidator | 15 | 45+ | 📝 TODO |
| `test_item_characteristics.py` | ItemCharacteristicsValidator | 13 | 40+ | 📝 TODO |
| `test_amount_basis.py` | AmountBasisValidator | 21 | 60+ | 📝 TODO |
| `test_amount_format.py` | AmountFormatValidator | 9 | 30+ | 📝 TODO |
| `test_frequency_alignment.py` | FrequencyAlignmentValidator | 4 | 15+ | 📝 TODO |
| `test_pet_validation.py` | PetValidation | 5 | 15+ | 📝 TODO |
| `test_parking_validation.py` | ParkingValidation | 4 | 12+ | 📝 TODO |
| `test_storage_validation.py` | StorageValidation | 3 | 10+ | 📝 TODO |
| `test_cross_validation.py` | CrossValidation | 13 | 40+ | 📝 TODO |
| `test_data_quality.py` | DataQualityValidator | 10 | 30+ | 📝 TODO |

**Total**: 110+ rules, 350+ test cases planned

## Test Patterns

### 1. Positive Tests (Valid Scenarios)
- Minimal valid cases
- Complete valid cases with all fields
- Edge cases that should pass
- Multiple valid variations

### 2. Negative Tests (Invalid Scenarios)
- Missing required fields
- Invalid values/formats
- Constraint violations
- Boundary condition failures

### 3. Test Structure

```python
class TestRuleName:
    """Test rule_name rule."""
    
    def test_valid_case(self, fixtures):
        """Valid scenario - should pass."""
        # Arrange
        xml = create_test_xml()
        
        # Act
        result = validate(xml)
        
        # Assert
        assert result.valid is True
        assert not any("rule_name" in e.rule_id for e in result.errors)
    
    def test_invalid_case(self, fixtures):
        """Invalid scenario - should fail."""
        xml = create_invalid_xml()
        result = validate(xml)
        
        assert result.valid is False
        assert any("rule_name" in e.rule_id for e in result.errors)
```

## Running Tests

### Run All Tests
```bash
pytest tests/validators/mits/ -v
```

### Run Specific Validator
```bash
pytest tests/validators/mits/test_xml_structure.py -v
```

### Run with Coverage
```bash
pytest tests/validators/mits/ --cov=app/validators/mits --cov-report=html --cov-report=term
```

### Run in Docker
```bash
docker-compose run --rm api pytest tests/validators/mits/ -v --cov=app/validators/mits
```

## Test Fixtures (conftest.py)

### Helper Functions
- `parse_xml()` - Parse XML strings
- `create_physical_property()` - Create PhysicalProperty wrapper
- `create_property()` - Create Property element
- `create_charge_class()` - Create ChargeOfferClass
- `create_charge_item()` - Create ChargeOfferItem
- `create_pet_item()` - Create PetOfferItem
- `create_parking_item()` - Create ParkingOfferItem
- `create_storage_item()` - Create StorageOfferItem

### Assertion Helpers
- `assert_has_error()` - Assert specific error exists
- `assert_no_errors()` - Assert no validation errors

## Rule Coverage Checklist

### XML Structure (6 rules)
- [x] xml_wellformed
- [x] xml_encoding_utf8
- [x] root_is_physical_property
- [x] property_exists
- [x] property_has_id
- [x] property_id_unique

### Fee Hierarchy (4 rules)
- [x] fee_in_valid_parent
- [x] fee_uses_class_container
- [x] class_item_amount_structure
- [x] no_fee_outside_hierarchy

### Identity Uniqueness (4 rules)
- [x] building_id_unique
- [x] floorplan_id_unique
- [x] unit_id_unique
- [x] id_no_whitespace

### Charge Class (6 rules)
- [ ] class_has_code
- [ ] class_code_across_parents
- [ ] class_code_unique_in_parent
- [ ] class_has_items
- [ ] class_no_empty_children
- [ ] class_limits_optional

### Class Limits (6 rules)
- [ ] limit_max_occurrences_valid
- [ ] limit_max_amount_valid
- [ ] limit_applies_to_structure
- [ ] limit_internal_code_nonempty
- [ ] limit_characteristics_valid
- [ ] limit_both_optional

### Offer Item Structure (15 rules)
- [ ] item_has_internal_code
- [ ] item_internal_code_unique
- [ ] item_no_duplicate_semantics
- [ ] item_has_name
- [ ] item_has_description
- [ ] item_has_one_characteristics
- [ ] item_has_amount_blocks
- [ ] item_min_occurrence_valid
- [ ] item_max_occurrence_valid
- [ ] item_occurrence_range_valid
- [ ] item_amount_basis_required
- [ ] item_percentage_code_when_needed
- [ ] item_amount_per_type_valid
- [ ] item_pms_fields_optional
- [x] ~~item_no_unexpected_children~~ (REMOVED - Rule 41 no longer enforced)

### Item Characteristics (13 rules + sub-rules)
- [ ] char_requirement_required
- [ ] char_conditional_scope_valid
- [ ] char_conditional_has_codes
- [ ] char_conditional_code_exists
- [ ] char_no_self_reference
- [ ] char_no_circular_reference
- [ ] char_lifecycle_required
- [ ] char_frequency_valid
- [ ] char_refundability_valid
- [ ] char_refund_details_required
- [ ] char_refund_max_type_required
- [ ] char_refund_max_required
- [ ] char_refund_per_type_valid

### Amount Basis (21 rules + sub-rules)
- [ ] basis_enum_valid
- [ ] basis_explicit_has_amounts
- [ ] basis_explicit_amounts_nonempty
- [ ] basis_explicit_percentage_empty
- [ ] basis_percentage_structure
- [ ] basis_percentage_has_value
- [ ] basis_percentage_amounts_empty
- [ ] basis_percentage_has_code
- [ ] basis_percentage_no_circular
- [ ] basis_range_one_amount
- [ ] basis_range_single_value
- [ ] basis_stepped_multiple_amounts
- [ ] basis_stepped_min_two
- [ ] basis_stepped_order_valid
- [ ] basis_stepped_zero_allowed
- [ ] basis_variable_either_or
- [ ] basis_variable_not_both
- [ ] basis_included_empty
- [ ] basis_included_no_basis
- [ ] basis_included_amounts_empty
- [ ] basis_included_percentage_empty

### Amount Format (9 rules + sub-rules)
- [ ] amount_has_value
- [ ] amount_decimal_format
- [ ] amount_non_negative
- [ ] percentage_decimal_valid
- [ ] percentage_over_100_allowed
- [ ] term_basis_valid
- [ ] date_range_valid
- [ ] scheduled_pricing_valid
- [ ] duration_integer_valid

### Frequency Alignment (4 rules)
- [ ] amount_per_type_enum
- [ ] amount_per_applicant_note
- [ ] frequency_basis_coherent
- [ ] onetime_with_term_basis

### Pet Validation (5 rules)
- [ ] pet_optional_fields
- [ ] pet_allowed_enum
- [ ] pet_not_allowed_no_amount
- [ ] pet_weight_format
- [ ] pet_deposit_refund_required

### Parking Validation (4 rules)
- [ ] parking_optional_fields
- [ ] parking_included_semantics
- [ ] parking_electric_enum
- [ ] parking_space_enum

### Storage Validation (3 rules)
- [ ] storage_optional_fields
- [ ] storage_dimensions_valid
- [ ] storage_unit_recognized

### Cross Validation (13 rules)
- [ ] internal_code_unique_in_class
- [ ] class_code_unique_in_parent
- [ ] cross_level_isolation
- [ ] limit_applies_to_same_class
- [ ] limit_occurrence_cap_runtime
- [ ] limit_amount_cap_runtime
- [ ] limit_characteristics_filter
- [ ] limit_all_items_no_filter
- [ ] reference_code_exists
- [ ] reference_no_self
- [ ] reference_no_circular
- [ ] reference_not_included
- [ ] reference_no_overlap

### Data Quality (10 rules)
- [ ] text_required_nonempty
- [ ] numeric_no_symbols
- [ ] numeric_no_plus_sign
- [ ] text_no_control_chars
- [ ] text_normalize_crlf
- [ ] date_format_valid
- [ ] date_no_overlap_in_item
- [ ] date_overlap_warning
- [ ] frequency_not_with_period
- [ ] name_unique_in_class

## Next Steps

1. ✅ Create shared fixtures (`conftest.py`)
2. ✅ Implement XML structure tests (6 rules)
3. ✅ Implement fee hierarchy tests (4 rules)
4. ✅ Implement identity uniqueness tests (4 rules)
5. 📝 Implement charge class tests (6 rules)
6. 📝 Implement class limits tests (6 rules)
7. 📝 Implement offer item structure tests (15 rules)
8. 📝 Implement remaining validator tests
9. 📝 Run full test suite and measure coverage
10. 📝 Add integration tests for complex scenarios
11. 📝 Document any implementation gaps found during testing

