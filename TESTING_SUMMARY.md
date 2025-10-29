# MITS Validator Testing Summary

## Current Test Coverage Status

### ✅ Completed Test Files (3/15 validators)

#### 1. XML Structure Validator (`test_xml_structure.py`)
- **Rules Tested**: 6/6 (100%)
- **Test Cases**: 30+
- **Coverage**:
  - ✅ xml_wellformed - 6 tests (valid, malformed, empty, etc.)
  - ✅ xml_encoding_utf8 - 2 tests (UTF-8 valid, encoding errors)
  - ✅ root_is_physical_property - 3 tests (correct, wrong, custom root)
  - ✅ property_exists - 4 tests (exists, missing, multiple)
  - ✅ property_has_id - 6 tests (valid, missing, empty, whitespace)
  - ✅ property_id_unique - 6 tests (unique, duplicate, case-sensitive)

#### 2. Fee Hierarchy Validator (`test_fee_hierarchy.py`)
- **Rules Tested**: 4/4 (100%)
- **Test Cases**: 15+
- **Coverage**:
  - ✅ fee_in_valid_parent - 5 tests (Property, Building, Floorplan, Unit, invalid)
  - ✅ fee_uses_class_container - 2 tests (in class, not in class)
  - ✅ class_item_amount_structure - 2 tests (valid, nested)
  - ✅ no_fee_outside_hierarchy - 3 tests (single, multiple, multi-level)

#### 3. Identity Uniqueness Validator (`test_identity_uniqueness.py`)
- **Rules Tested**: 4/4 (100%)
- **Test Cases**: 15+
- **Coverage**:
  - ✅ building_id_unique - 4 tests (unique, duplicate, none, single)
  - ✅ floorplan_id_unique - 3 tests (unique, duplicate, across buildings)
  - ✅ unit_id_unique - 3 tests (unique, duplicate, across floorplans)
  - ✅ id_no_whitespace - 4 tests (no whitespace, various whitespace types)

### 📝 TODO: Remaining Test Files (12/15 validators)

#### 4. Charge Class Validator
- **Rules**: 6
- **Estimated Tests**: 20+
- **Priority**: HIGH (core validation logic)

#### 5. Class Limits Validator
- **Rules**: 6
- **Estimated Tests**: 20+
- **Priority**: HIGH (complex business rules)

#### 6. Offer Item Structure Validator
- **Rules**: 15 (largest validator)
- **Estimated Tests**: 45+
- **Priority**: HIGH (most rules, critical path)

#### 7. Item Characteristics Validator
- **Rules**: 13
- **Estimated Tests**: 40+
- **Priority**: HIGH (complex conditional logic)

#### 8. Amount Basis Validator
- **Rules**: 21 (most complex)
- **Estimated Tests**: 60+
- **Priority**: HIGH (most rules, intricate logic)

#### 9. Amount Format Validator
- **Rules**: 9
- **Estimated Tests**: 30+
- **Priority**: MEDIUM (format validation)

#### 10. Frequency Alignment Validator
- **Rules**: 4
- **Estimated Tests**: 15+
- **Priority**: MEDIUM (coherence checks)

#### 11. Pet Validation
- **Rules**: 5
- **Estimated Tests**: 15+
- **Priority**: MEDIUM (specialized items)

#### 12. Parking Validation
- **Rules**: 4
- **Estimated Tests**: 12+
- **Priority**: MEDIUM (specialized items)

#### 13. Storage Validation
- **Rules**: 3
- **Estimated Tests**: 10+
- **Priority**: MEDIUM (specialized items)

#### 14. Cross Validation
- **Rules**: 13
- **Estimated Tests**: 40+
- **Priority**: HIGH (integrity checks)

#### 15. Data Quality Validator
- **Rules**: 10
- **Estimated Tests**: 30+
- **Priority**: MEDIUM (hygiene checks)

## Test Infrastructure

### Shared Fixtures (`conftest.py`)
- ✅ `parse_xml()` - Parse XML strings safely
- ✅ `create_physical_property()` - Create root wrapper
- ✅ `create_property()` - Create Property element
- ✅ `create_charge_class()` - Create ChargeOfferClass
- ✅ `create_charge_item()` - Create ChargeOfferItem with defaults
- ✅ `create_pet_item()` - Create PetOfferItem
- ✅ `create_parking_item()` - Create ParkingOfferItem
- ✅ `create_storage_item()` - Create StorageOfferItem
- ✅ `assert_has_error()` - Assert specific error exists
- ✅ `assert_no_errors()` - Assert validation passes

### Test Patterns
Each test follows a consistent structure:
```python
def test_rule_name_scenario(self, fixtures):
    """Description of test scenario."""
    # Arrange
    xml = create_test_xml()
    root = parse_xml(xml)
    validator = ValidatorClass(root)
    
    # Act
    result = validator.validate()
    
    # Assert
    assert result.valid is True/False
    assert any/not any("rule_id" in e.rule_id for e in result.errors)
```

## Running Tests

### Docker (Recommended)
```bash
# Run all tests
docker-compose run --rm api pytest tests/validators/mits/ -v

# Run specific validator
docker-compose run --rm api pytest tests/validators/mits/test_xml_structure.py -v

# Run with coverage
docker-compose run --rm api pytest tests/validators/mits/ --cov=app/validators/mits --cov-report=html
```

### Local (if dependencies installed)
```bash
pytest tests/validators/mits/ -v
pytest tests/validators/mits/ --cov=app/validators/mits --cov-report=term
```

## Coverage Goals

- **Current**: ~12% of rules tested (14/110)
- **Target**: >90% line and branch coverage
- **Estimated Remaining Work**: 12 test files, 350+ test cases

## Recommendations

### Phase 1: High Priority Validators (Core Logic)
1. `test_charge_class.py` - 6 rules
2. `test_class_limits.py` - 6 rules
3. `test_offer_item_structure.py` - 15 rules
4. `test_item_characteristics.py` - 13 rules
5. `test_amount_basis.py` - 21 rules
6. `test_cross_validation.py` - 13 rules

**Subtotal**: 74 rules (67% of total)

### Phase 2: Medium Priority Validators (Format & Specialized)
7. `test_amount_format.py` - 9 rules
8. `test_frequency_alignment.py` - 4 rules
9. `test_pet_validation.py` - 5 rules
10. `test_parking_validation.py` - 4 rules
11. `test_storage_validation.py` - 3 rules
12. `test_data_quality.py` - 10 rules

**Subtotal**: 35 rules (32% of total)

### Phase 3: Integration & Edge Cases
- Complex multi-validator scenarios
- Performance tests
- Fuzzing/property-based tests
- Regression tests

## Test Metrics Tracking

### Per Validator
- Line coverage %
- Branch coverage %
- Number of test cases
- Number of rules covered
- Positive/negative test ratio

### Overall
- Total line coverage
- Total branch coverage
- Test execution time
- Number of assertions
- Mutation test score (optional)

## Benefits of Current Test Infrastructure

1. **Reusable Fixtures**: Reduces boilerplate in individual tests
2. **Consistent Patterns**: Easy to add new tests following established patterns
3. **Clear Documentation**: Each test has descriptive name and docstring
4. **Isolated Tests**: Each test focuses on single rule or scenario
5. **Fast Feedback**: Can run individual validator tests quickly

## Next Steps

1. ✅ Create TEST_PLAN.md with full rule mapping
2. ✅ Create conftest.py with shared fixtures
3. ✅ Implement xml_structure tests (6 rules)
4. ✅ Implement fee_hierarchy tests (4 rules)
5. ✅ Implement identity_uniqueness tests (4 rules)
6. 📝 **NEXT**: Implement charge_class tests (6 rules)
7. 📝 Continue with remaining validators
8. 📝 Run full test suite and measure coverage
9. 📝 Address any gaps found during testing
10. 📝 Add integration tests
11. 📝 Set up CI to enforce coverage thresholds

## Continuous Improvement

- Add tests for bugs as they're discovered
- Update tests when validation rules change
- Monitor and improve test execution time
- Consider property-based testing with Hypothesis
- Add mutation testing to verify test quality

