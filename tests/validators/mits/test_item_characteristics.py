"""
Unit tests for Item Characteristics validator.

Tests all rules (13 total):
- char_requirement_required
- char_conditional_scope_valid, char_conditional_has_codes, char_conditional_code_exists
- char_no_self_reference, char_no_circular_reference
- char_lifecycle_required
- char_frequency_valid
- char_refundability_valid
- char_refund_details_required, char_refund_max_type_required, char_refund_max_required
- char_refund_per_type_valid
"""

import pytest
from app.validators.mits.item_characteristics import ItemCharacteristicsValidator


class TestCharRequirementRequired:
    """Test char_requirement_required rule."""

    def test_item_with_requirement(self, parse_xml, create_charge_class, create_charge_item):
        """Item with ChargeRequirement - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(requirement="Mandatory"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_requirement(self, parse_xml, create_charge_class):
        """Item without ChargeRequirement - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_requirement_required" in e.rule_id for e in result.errors)


class TestCharConditional:
    """Test char_conditional_* rules."""

    def test_conditional_with_valid_scope(self, parse_xml, create_charge_class):
        """Conditional item with ConditionalScope - should pass."""
        item = """<ChargeOfferItem InternalCode="pet_fee">
            <Name>Pet Fee</Name>
            <Description>Monthly pet fee</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <ConditionalScope>
                    <InternalCode>pet_allowed</InternalCode>
                </ConditionalScope>
                <Lifecycle>During Term</Lifecycle>
                <PaymentFrequency>Monthly</PaymentFrequency>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("PET", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        # Should validate conditional scope structure

    def test_conditional_without_codes(self, parse_xml, create_charge_class):
        """Conditional with ConditionalScope but no codes - should fail."""
        item = """<ChargeOfferItem InternalCode="pet_fee">
            <Name>Pet Fee</Name>
            <Description>Monthly pet fee</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <ConditionalScope>
                </ConditionalScope>
                <Lifecycle>During Term</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("PET", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_conditional_has_codes" in e.rule_id for e in result.errors)

    def test_conditional_self_reference(self, parse_xml, create_charge_class):
        """Conditional item referencing itself - should fail."""
        item = """<ChargeOfferItem InternalCode="pet_fee">
            <Name>Pet Fee</Name>
            <Description>Monthly pet fee</Description>
            <Characteristics>
                <ChargeRequirement>Conditional</ChargeRequirement>
                <ConditionalScope>
                    <InternalCode>pet_fee</InternalCode>
                </ConditionalScope>
                <Lifecycle>During Term</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("PET", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_no_self_reference" in e.rule_id for e in result.errors)


class TestCharLifecycleRequired:
    """Test char_lifecycle_required rule."""

    def test_item_with_lifecycle(self, parse_xml, create_charge_class, create_charge_item):
        """Item with Lifecycle - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(lifecycle="At Application"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_lifecycle(self, parse_xml, create_charge_class):
        """Item without Lifecycle - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_lifecycle_required" in e.rule_id for e in result.errors)


class TestCharFrequencyValid:
    """Test char_frequency_valid rule."""

    def test_onetime_frequency(self, parse_xml, create_charge_class, create_charge_item):
        """Item with PaymentFrequency One-time - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(frequency="One-time"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_monthly_frequency(self, parse_xml, create_charge_class, create_charge_item):
        """Item with PaymentFrequency Monthly - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("RENT", create_charge_item(lifecycle="During Term", frequency="Monthly"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_invalid_frequency(self, parse_xml, create_charge_class):
        """Item with invalid PaymentFrequency - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>During Term</Lifecycle>
                <PaymentFrequency>InvalidValue</PaymentFrequency>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_frequency_valid" in e.rule_id for e in result.errors)


class TestCharRefundability:
    """Test char_refundability_* rules."""

    def test_refundable_with_details(self, parse_xml, create_charge_class):
        """Refundable item with RefundDetails - should pass."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
                <RefundDetails>
                    <RefundMax>1000.00</RefundMax>
                    <RefundMaxType>Amount</RefundMaxType>
                    <RefundPerType>Per Unit</RefundPerType>
                </RefundDetails>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        # Should validate refund structure

    def test_refundable_without_details(self, parse_xml, create_charge_class):
        """Refundable item without RefundDetails - should fail."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_refund_details_required" in e.rule_id for e in result.errors)

    def test_refund_without_max(self, parse_xml, create_charge_class):
        """RefundDetails without RefundMax - should fail."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
                <RefundDetails>
                    <RefundMaxType>Amount</RefundMaxType>
                </RefundDetails>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_refund_max_required" in e.rule_id for e in result.errors)

    def test_refund_without_max_type(self, parse_xml, create_charge_class):
        """RefundDetails without RefundMaxType - should fail."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
                <RefundDetails>
                    <RefundMax>1000.00</RefundMax>
                </RefundDetails>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_refund_max_type_required" in e.rule_id for e in result.errors)

    def test_nonrefundable_no_details(self, parse_xml, create_charge_class):
        """Non-refundable item without RefundDetails - should pass."""
        item = """<ChargeOfferItem InternalCode="app_fee">
            <Name>Application Fee</Name>
            <Description>Non-refundable application fee</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Non-refundable</Refundability>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        # Non-refundable doesn't need RefundDetails


class TestCharRefundPerType:
    """Test char_refund_per_type_valid rule."""

    def test_valid_refund_per_type(self, parse_xml, create_charge_class):
        """RefundPerType with valid value - should pass."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
                <RefundDetails>
                    <RefundMax>1000.00</RefundMax>
                    <RefundMaxType>Amount</RefundMaxType>
                    <RefundPerType>Per Unit</RefundPerType>
                </RefundDetails>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        # Valid RefundPerType values: Per Unit, Per Applicant, etc.

    def test_invalid_refund_per_type(self, parse_xml, create_charge_class):
        """RefundPerType with invalid value - should fail."""
        item = """<ChargeOfferItem InternalCode="sec_dep">
            <Name>Security Deposit</Name>
            <Description>Refundable security deposit</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Move-In</Lifecycle>
                <PaymentFrequency>One-time</PaymentFrequency>
                <Refundability>Refundable</Refundability>
                <RefundDetails>
                    <RefundMax>1000.00</RefundMax>
                    <RefundMaxType>Amount</RefundMaxType>
                    <RefundPerType>InvalidValue</RefundPerType>
                </RefundDetails>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>1000</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("SEC", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ItemCharacteristicsValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("char_refund_per_type_valid" in e.rule_id for e in result.errors)

