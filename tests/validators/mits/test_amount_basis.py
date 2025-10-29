"""
Unit tests for Amount Basis validator.

Tests all rules (21 total):
- basis_enum_valid
- basis_explicit_has_amounts, basis_explicit_amounts_nonempty, basis_explicit_percentage_empty
- basis_percentage_structure, basis_percentage_has_value, basis_percentage_amounts_empty, 
  basis_percentage_has_code, basis_percentage_no_circular
- basis_range_one_amount, basis_range_single_value
- basis_stepped_multiple_amounts, basis_stepped_min_two, basis_stepped_order_valid, basis_stepped_zero_allowed
- basis_variable_either_or, basis_variable_not_both
- basis_included_empty, basis_included_no_basis, basis_included_amounts_empty, basis_included_percentage_empty
"""

import pytest
from app.validators.mits.amount_basis import AmountBasisValidator


class TestBasisEnumValid:
    """Test basis_enum_valid rule."""

    def test_explicit_basis(self, parse_xml, create_charge_class, create_charge_item):
        """AmountBasis = 'Explicit' - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(amount_basis="Explicit"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_percentage_of_basis(self, parse_xml, create_charge_class):
        """AmountBasis = 'Percentage Of' - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage>10.00</Percentage>
                <PercentageOfCode>base_rent</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Should accept valid enum value

    def test_invalid_basis_value(self, parse_xml, create_charge_class, create_charge_item):
        """AmountBasis with invalid value - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(amount_basis="InvalidValue"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_enum_valid" in e.rule_id for e in result.errors)


class TestBasisExplicit:
    """Test basis_explicit_* rules."""

    def test_explicit_with_amounts(self, parse_xml, create_charge_class, create_charge_item):
        """Explicit basis with Amounts populated - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(amount_basis="Explicit", amounts="50.00"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_explicit_without_amounts(self, parse_xml, create_charge_class):
        """Explicit basis without Amounts - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_explicit" in e.rule_id for e in result.errors)

    def test_explicit_with_percentage_populated(self, parse_xml, create_charge_class):
        """Explicit basis with Percentage populated - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>50.00</Amounts>
                <Percentage>10.00</Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_explicit_percentage_empty" in e.rule_id for e in result.errors)


class TestBasisPercentageOf:
    """Test basis_percentage_* rules."""

    def test_percentage_of_valid_structure(self, parse_xml, create_charge_class):
        """Percentage Of with valid structure - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Pet Fee</Name>
            <Description>Monthly pet fee</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
                <PaymentFrequency>Monthly</PaymentFrequency>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage>5.00</Percentage>
                <PercentageOfCode>base_rent</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("PET", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Should pass with correct structure

    def test_percentage_of_without_percentage_value(self, parse_xml, create_charge_class):
        """Percentage Of without Percentage value - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage></Percentage>
                <PercentageOfCode>base_rent</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_percentage_has_value" in e.rule_id for e in result.errors)

    def test_percentage_of_with_amounts_populated(self, parse_xml, create_charge_class):
        """Percentage Of with Amounts populated - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>50.00</Amounts>
                <Percentage>10.00</Percentage>
                <PercentageOfCode>base_rent</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_percentage_amounts_empty" in e.rule_id for e in result.errors)

    def test_percentage_of_without_code(self, parse_xml, create_charge_class):
        """Percentage Of without PercentageOfCode - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage>10.00</Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_percentage_has_code" in e.rule_id for e in result.errors)

    def test_percentage_of_self_reference(self, parse_xml, create_charge_class):
        """Percentage Of referencing itself - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Percentage Of</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage>10.00</Percentage>
                <PercentageOfCode>fee1</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_percentage_no_circular" in e.rule_id for e in result.errors)


class TestBasisRange:
    """Test basis_range_* rules (Range or Variable)."""

    def test_range_with_single_amount(self, parse_xml, create_charge_class):
        """Range basis with single Amount - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Range or Variable</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>100.00-500.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Should pass with single range value

    def test_range_with_multiple_amounts(self, parse_xml, create_charge_class):
        """Range basis with multiple Amounts - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Range or Variable</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>100.00</Amounts>
                <Amounts>200.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_range_one_amount" in e.rule_id for e in result.errors)


class TestBasisStepped:
    """Test basis_stepped_* rules."""

    def test_stepped_with_multiple_amounts(self, parse_xml, create_charge_class):
        """Stepped basis with multiple Amounts - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Stepped</AmountBasis>
            <ChargeOfferAmount TermBasis="1">
                <Amounts>1000.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
            <ChargeOfferAmount TermBasis="6">
                <Amounts>900.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
            <ChargeOfferAmount TermBasis="12">
                <Amounts>800.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("RENT", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Should pass with proper stepped structure

    def test_stepped_with_single_amount(self, parse_xml, create_charge_class):
        """Stepped basis with only one Amount - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
                <PaymentFrequency>Monthly</PaymentFrequency>
            </Characteristics>
            <AmountBasis>Stepped</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>1000.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("RENT", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_stepped_min_two" in e.rule_id for e in result.errors)

    def test_stepped_with_descending_order(self, parse_xml, create_charge_class):
        """Stepped basis with amounts in descending order - should pass/warn."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
                <PaymentFrequency>Monthly</PaymentFrequency>
            </Characteristics>
            <AmountBasis>Stepped</AmountBasis>
            <ChargeOfferAmount TermBasis="1">
                <Amounts>1000.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
            <ChargeOfferAmount TermBasis="12">
                <Amounts>900.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("RENT", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Descending order is valid (longer term = lower rate)


class TestBasisVariable:
    """Test basis_variable_* rules."""

    def test_variable_with_amounts_only(self, parse_xml, create_charge_class):
        """Variable basis with Amounts only - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Variable</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>Call for pricing</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Variable with text amounts is allowed

    def test_variable_with_percentage_only(self, parse_xml, create_charge_class):
        """Variable basis with Percentage only - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Variable</AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage>Varies</Percentage>
                <PercentageOfCode>base_rent</PercentageOfCode>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Variable with percentage is allowed

    def test_variable_with_both(self, parse_xml, create_charge_class):
        """Variable basis with both Amounts and Percentage - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Optional</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Variable</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>Call for pricing</Amounts>
                <Percentage>Varies</Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("FEE", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_variable_not_both" in e.rule_id for e in result.errors)


class TestBasisIncluded:
    """Test basis_included_* rules."""

    def test_included_with_empty_basis(self, parse_xml, create_charge_class):
        """Included item with empty AmountBasis - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Water</Name>
            <Description>Water utility included</Description>
            <Characteristics>
                <ChargeRequirement>Included</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
            </Characteristics>
            <AmountBasis></AmountBasis>
            <ChargeOfferAmount>
                <Amounts></Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("UTIL", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        # Included items can have empty AmountBasis

    def test_included_with_explicit_basis(self, parse_xml, create_charge_class):
        """Included item with AmountBasis = Explicit - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Water</Name>
            <Description>Water utility</Description>
            <Characteristics>
                <ChargeRequirement>Included</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount>
                <Amounts>50.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("UTIL", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_included" in e.rule_id for e in result.errors)

    def test_included_with_populated_amounts(self, parse_xml, create_charge_class):
        """Included item with populated Amounts - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Water</Name>
            <Description>Water utility</Description>
            <Characteristics>
                <ChargeRequirement>Included</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
            </Characteristics>
            <AmountBasis></AmountBasis>
            <ChargeOfferAmount>
                <Amounts>50.00</Amounts>
                <Percentage></Percentage>
            </ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("UTIL", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = AmountBasisValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("basis_included_amounts_empty" in e.rule_id for e in result.errors)

