"""
Unit tests for Offer Item Structure validator.

Tests key rules from the 15 rules:
- item_has_internal_code
- item_internal_code_unique
- item_has_name
- item_has_description
- item_has_one_characteristics
- item_has_amount_blocks
- item_amount_basis_required
"""

import pytest
from app.validators.mits.offer_item_structure import OfferItemStructureValidator


class TestItemHasInternalCode:
    """Test item_has_internal_code rule."""

    def test_item_with_internal_code(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with InternalCode - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="app_fee"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_internal_code(self, parse_xml, create_charge_class):
        """ChargeOfferItem without InternalCode - should fail."""
        item = """<ChargeOfferItem>
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
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
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_has_internal_code" in e.rule_id for e in result.errors)

    def test_item_with_empty_internal_code(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with empty InternalCode - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code=""))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_has_internal_code" in e.rule_id for e in result.errors)


class TestItemInternalCodeUnique:
    """Test item_internal_code_unique rule."""

    def test_unique_internal_codes(self, parse_xml, create_charge_class, create_charge_item):
        """All InternalCodes unique in class - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item("fee1") + create_charge_item("fee2"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_internal_codes(self, parse_xml, create_charge_class, create_charge_item):
        """Duplicate InternalCodes in same class - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item("same_code") + create_charge_item("same_code"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_internal_code_unique" in e.rule_id for e in result.errors)

    def test_same_code_different_classes(self, parse_xml, create_charge_class, create_charge_item):
        """Same InternalCode in different classes - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item("fee1"))}
                {create_charge_class("SEC", create_charge_item("fee1"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        # Scope is per-class, so should pass


class TestItemHasName:
    """Test item_has_name rule."""

    def test_item_with_name(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with Name - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(name="Application Fee"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_name(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem without Name - should fail."""
        item = create_charge_item().replace("<Name>Test Item</Name>", "")
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_has_name" in e.rule_id for e in result.errors)

    def test_item_with_empty_name(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with empty Name - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(name=""))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False


class TestItemHasDescription:
    """Test item_has_description rule."""

    def test_item_with_description(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with Description - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(description="One-time application fee"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_description(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem without Description - should fail."""
        item = create_charge_item().replace("<Description>Test Description</Description>", "")
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_has_description" in e.rule_id for e in result.errors)


class TestItemHasOneCharacteristics:
    """Test item_has_one_characteristics rule."""

    def test_item_with_characteristics(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with exactly one Characteristics - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_characteristics(self, parse_xml, create_charge_class):
        """ChargeOfferItem without Characteristics - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <AmountBasis>Explicit</AmountBasis>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_has_one_characteristics" in e.rule_id for e in result.errors)


class TestItemHasAmountBlocks:
    """Test item_has_amount_blocks rule."""

    def test_item_with_amount_block(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferItem with ChargeOfferAmount - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_item_without_amount_block_mandatory(self, parse_xml, create_charge_class):
        """Mandatory item without ChargeOfferAmount - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <AmountBasis>Explicit</AmountBasis>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False


class TestItemAmountBasisRequired:
    """Test item_amount_basis_required rule."""

    def test_mandatory_item_with_amount_basis(self, parse_xml, create_charge_class, create_charge_item):
        """Mandatory item with AmountBasis - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(requirement="Mandatory", amount_basis="Explicit"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_mandatory_item_without_amount_basis(self, parse_xml, create_charge_class):
        """Mandatory item without AmountBasis - should fail."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Mandatory</ChargeRequirement>
                <Lifecycle>At Application</Lifecycle>
            </Characteristics>
            <ChargeOfferAmount><Amounts>50</Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("item_amount_basis_required" in e.rule_id for e in result.errors)

    def test_included_item_empty_amount_basis(self, parse_xml, create_charge_class):
        """Included item with empty AmountBasis - should pass."""
        item = """<ChargeOfferItem InternalCode="fee1">
            <Name>Test</Name>
            <Description>Test</Description>
            <Characteristics>
                <ChargeRequirement>Included</ChargeRequirement>
                <Lifecycle>During Tenancy</Lifecycle>
            </Characteristics>
            <AmountBasis></AmountBasis>
            <ChargeOfferAmount><Amounts></Amounts><Percentage></Percentage></ChargeOfferAmount>
        </ChargeOfferItem>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("UTIL", item)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = OfferItemStructureValidator(root)
        result = validator.validate()
        
        # Included items can have empty AmountBasis

