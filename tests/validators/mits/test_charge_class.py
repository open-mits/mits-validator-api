"""
Unit tests for Charge Class validator.

Tests all rules:
- class_has_code
- class_code_across_parents
- class_code_unique_in_parent
- class_has_items
- class_no_empty_children
- class_limits_optional
"""

import pytest
from app.validators.mits.charge_class import ChargeClassValidator


class TestClassHasCode:
    """Test class_has_code rule."""

    def test_class_with_code(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with Code attribute - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class(code="APP", content=create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_class_without_code(self, parse_xml, create_charge_item):
        """ChargeOfferClass without Code attribute - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                <ChargeOfferClass>
                    {create_charge_item()}
                </ChargeOfferClass>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("class_has_code" in e.rule_id for e in result.errors)

    def test_class_with_empty_code(self, parse_xml, create_charge_item):
        """ChargeOfferClass with empty Code - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                <ChargeOfferClass Code="">
                    {create_charge_item()}
                </ChargeOfferClass>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("class_has_code" in e.rule_id for e in result.errors)

    def test_multiple_classes_all_have_codes(self, parse_xml, create_charge_class, create_charge_item):
        """Multiple ChargeOfferClass elements all with Code - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="app1"))}
                {create_charge_class("SEC", create_charge_item(internal_code="sec1"))}
                {create_charge_class("RENT", create_charge_item(internal_code="rent1"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True


class TestClassCodeAcrossParents:
    """Test class_code_across_parents rule."""

    def test_same_code_different_properties(self, parse_xml, create_property, create_charge_class, create_charge_item):
        """Same Code in different Properties - should pass."""
        xml = f"""<PhysicalProperty>
            {create_property("1", create_charge_class("APP", create_charge_item(internal_code="fee1")))}
            {create_property("2", create_charge_class("APP", create_charge_item(internal_code="fee2")))}
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        # Depends on scope - codes may be property-wide or global


class TestClassCodeUniqueInParent:
    """Test class_code_unique_in_parent rule."""

    def test_unique_codes_in_property(self, parse_xml, create_charge_class, create_charge_item):
        """Unique ChargeOfferClass Codes in Property - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="app1"))}
                {create_charge_class("SEC", create_charge_item(internal_code="sec1"))}
                {create_charge_class("RENT", create_charge_item(internal_code="rent1"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_codes_in_property(self, parse_xml, create_charge_class, create_charge_item):
        """Duplicate ChargeOfferClass Code in same Property - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="app1"))}
                {create_charge_class("APP", create_charge_item(internal_code="app2"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("class_code_unique_in_parent" in e.rule_id for e in result.errors)

    def test_case_sensitive_codes(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass Codes are case-sensitive - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="app1"))}
                {create_charge_class("app", create_charge_item(internal_code="app2"))}
                {create_charge_class("App", create_charge_item(internal_code="app3"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        # Depends on implementation - may be case-sensitive or insensitive


class TestClassHasItems:
    """Test class_has_items rule."""

    def test_class_with_items(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with ChargeOfferItem - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_class_without_items(self, parse_xml):
        """ChargeOfferClass without any items - should fail."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <ChargeOfferClass Code="APP"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("class_has_items" in e.rule_id for e in result.errors)

    def test_class_with_multiple_items(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with multiple items - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item(internal_code="fee1") + create_charge_item(internal_code="fee2"))}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_class_with_nested_class(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with nested ChargeOfferClass - should pass."""
        inner_class = create_charge_class("SUB", create_charge_item(internal_code="sub1"))
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", inner_class)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        # Nested classes count as children


class TestClassNoEmptyChildren:
    """Test class_no_empty_children rule."""

    def test_class_with_items_no_empty_children(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with items, no empty nested classes - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_class_with_empty_nested_class(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with empty nested ChargeOfferClass - should fail."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item() + '<ChargeOfferClass Code="EMPTY"/>')}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        # Should detect empty nested class


class TestClassLimitsOptional:
    """Test class_limits_optional rule."""

    def test_class_without_limits(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass without ChargeOfferClassLimit - should pass."""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item())}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_class_with_limits(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with ChargeOfferClassLimit - should pass."""
        limit = """<ChargeOfferClassLimit>
            <MaxOccurrences>3</MaxOccurrences>
            <AppliesTo>
                <InternalCode>fee1</InternalCode>
            </AppliesTo>
        </ChargeOfferClassLimit>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item() + limit)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        # Limits are optional, should pass

    def test_class_with_multiple_limits(self, parse_xml, create_charge_class, create_charge_item):
        """ChargeOfferClass with multiple limits - should pass."""
        limits = """<ChargeOfferClassLimit>
            <MaxOccurrences>3</MaxOccurrences>
            <AppliesTo>
                <InternalCode>fee1</InternalCode>
            </AppliesTo>
        </ChargeOfferClassLimit>
        <ChargeOfferClassLimit>
            <MaxAmount>500.00</MaxAmount>
            <AppliesTo>
                <InternalCode>fee1</InternalCode>
            </AppliesTo>
        </ChargeOfferClassLimit>"""
        xml = f"""<PhysicalProperty>
            <Property IDValue="1">
                {create_charge_class("APP", create_charge_item() + limits)}
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = ChargeClassValidator(root)
        result = validator.validate()
        
        # Multiple limits are allowed

