"""
Unit tests for XML Structure validator.

Tests all rules:
- xml_wellformed
- xml_encoding_utf8
- root_is_physical_property
- property_exists
- property_has_id
- property_id_unique
"""

import pytest
from defusedxml import ElementTree as ET

from app.validators.mits.xml_structure import XmlStructureValidator, validate_xml_wellformed


class TestXmlWellformed:
    """Test xml_wellformed and xml_encoding_utf8 rules."""

    def test_valid_xml(self):
        """Valid XML should pass."""
        xml = '<?xml version="1.0" encoding="UTF-8"?><PhysicalProperty><Property IDValue="1"/></PhysicalProperty>'
        result = validate_xml_wellformed(xml)
        assert result.valid is True
        assert len(result.errors) == 0

    def test_malformed_xml_unclosed_tag(self):
        """Malformed XML with unclosed tag should fail."""
        xml = '<?xml version="1.0" encoding="UTF-8"?><PhysicalProperty><Property>'
        result = validate_xml_wellformed(xml)
        assert result.valid is False
        assert any("xml_wellformed" in e.rule_id for e in result.errors)

    def test_malformed_xml_invalid_structure(self):
        """Invalid XML structure should fail."""
        xml = '<?xml version="1.0" encoding="UTF-8"?><Property></PhysicalProperty>'
        result = validate_xml_wellformed(xml)
        assert result.valid is False
        assert any("xml_wellformed" in e.rule_id for e in result.errors)

    def test_malformed_xml_invalid_char(self):
        """XML with invalid characters should fail."""
        xml = '<?xml version="1.0" encoding="UTF-8"?><PhysicalProperty><<</PhysicalProperty>'
        result = validate_xml_wellformed(xml)
        assert result.valid is False

    def test_utf8_encoding(self):
        """Valid UTF-8 encoding should pass."""
        xml = '<?xml version="1.0" encoding="UTF-8"?><PhysicalProperty><Property IDValue="tëst"/></PhysicalProperty>'
        result = validate_xml_wellformed(xml)
        assert result.valid is True

    def test_empty_xml(self):
        """Empty XML should fail."""
        xml = ""
        result = validate_xml_wellformed(xml)
        assert result.valid is False


class TestRootIsPhysicalProperty:
    """Test root_is_physical_property rule."""

    def test_correct_root_element(self, parse_xml):
        """Root element is PhysicalProperty - should pass."""
        xml = '<PhysicalProperty><Property IDValue="1"/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True
        assert not any("root_is_physical_property" in e.rule_id for e in result.errors)

    def test_wrong_root_element(self, parse_xml):
        """Root element is not PhysicalProperty - should fail."""
        xml = '<Property IDValue="1"/>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("root_is_physical_property" in e.rule_id for e in result.errors)
        error = [e for e in result.errors if "root_is_physical_property" in e.rule_id][0]
        assert "Property" in error.message

    def test_wrong_root_custom_element(self, parse_xml):
        """Custom root element - should fail."""
        xml = '<Building><Property IDValue="1"/></Building>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("root_is_physical_property" in e.rule_id for e in result.errors)


class TestPropertyExists:
    """Test property_exists rule."""

    def test_property_exists(self, parse_xml):
        """PhysicalProperty contains Property - should pass."""
        xml = '<PhysicalProperty><Property IDValue="1"/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_no_property_element(self, parse_xml):
        """PhysicalProperty without Property - should fail."""
        xml = '<PhysicalProperty></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_exists" in e.rule_id for e in result.errors)

    def test_property_with_other_elements(self, parse_xml):
        """PhysicalProperty with Property and other elements - should pass."""
        xml = '<PhysicalProperty><Property IDValue="1"/><OtherElement/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_multiple_properties(self, parse_xml):
        """PhysicalProperty with multiple Properties - should pass."""
        xml = '<PhysicalProperty><Property IDValue="1"/><Property IDValue="2"/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True


class TestPropertyHasId:
    """Test property_has_id rule."""

    def test_property_with_id(self, parse_xml):
        """Property with IDValue - should pass."""
        xml = '<PhysicalProperty><Property IDValue="prop-123"/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_property_without_id(self, parse_xml):
        """Property without IDValue - should fail."""
        xml = '<PhysicalProperty><Property/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_has_id" in e.rule_id for e in result.errors)

    def test_property_with_empty_id(self, parse_xml):
        """Property with empty IDValue - should fail."""
        xml = '<PhysicalProperty><Property IDValue=""/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_has_id" in e.rule_id for e in result.errors)

    def test_property_with_whitespace_id(self, parse_xml):
        """Property with whitespace-only IDValue - should fail."""
        xml = '<PhysicalProperty><Property IDValue="   "/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_has_id" in e.rule_id for e in result.errors)

    def test_multiple_properties_all_have_ids(self, parse_xml):
        """Multiple Properties all with IDValues - should pass."""
        xml = '''<PhysicalProperty>
            <Property IDValue="1"/>
            <Property IDValue="2"/>
            <Property IDValue="3"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_multiple_properties_one_missing_id(self, parse_xml):
        """Multiple Properties, one missing IDValue - should fail."""
        xml = '''<PhysicalProperty>
            <Property IDValue="1"/>
            <Property/>
            <Property IDValue="3"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_has_id" in e.rule_id for e in result.errors)


class TestPropertyIdUnique:
    """Test property_id_unique rule."""

    def test_unique_property_ids(self, parse_xml):
        """All Property IDValues are unique - should pass."""
        xml = '''<PhysicalProperty>
            <Property IDValue="prop-1"/>
            <Property IDValue="prop-2"/>
            <Property IDValue="prop-3"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_property_ids(self, parse_xml):
        """Duplicate Property IDValues - should fail."""
        xml = '''<PhysicalProperty>
            <Property IDValue="prop-1"/>
            <Property IDValue="prop-2"/>
            <Property IDValue="prop-1"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("property_id_unique" in e.rule_id for e in result.errors)
        error = [e for e in result.errors if "property_id_unique" in e.rule_id][0]
        assert "prop-1" in error.message

    def test_multiple_duplicates(self, parse_xml):
        """Multiple sets of duplicate IDs - should report all."""
        xml = '''<PhysicalProperty>
            <Property IDValue="prop-1"/>
            <Property IDValue="prop-2"/>
            <Property IDValue="prop-1"/>
            <Property IDValue="prop-2"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        unique_errors = [e for e in result.errors if "property_id_unique" in e.rule_id]
        assert len(unique_errors) >= 2  # At least 2 duplicate errors

    def test_case_sensitive_ids(self, parse_xml):
        """Property IDs are case-sensitive - should pass."""
        xml = '''<PhysicalProperty>
            <Property IDValue="prop-1"/>
            <Property IDValue="PROP-1"/>
            <Property IDValue="Prop-1"/>
        </PhysicalProperty>'''
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_single_property_always_unique(self, parse_xml):
        """Single Property is always unique - should pass."""
        xml = '<PhysicalProperty><Property IDValue="only-one"/></PhysicalProperty>'
        root = parse_xml(xml)
        validator = XmlStructureValidator(root)
        result = validator.validate()
        
        assert result.valid is True

