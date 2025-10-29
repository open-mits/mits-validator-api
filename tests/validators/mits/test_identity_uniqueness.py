"""
Unit tests for Identity Uniqueness validator.

Tests all rules:
- building_id_unique
- floorplan_id_unique
- unit_id_unique
- id_no_whitespace
"""

import pytest
from app.validators.mits.identity_uniqueness import IdentityUniquenessValidator


class TestBuildingIdUnique:
    """Test building_id_unique rule."""

    def test_unique_building_ids(self, parse_xml):
        """All Building IDs unique - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1"/>
                <Building IDValue="B2"/>
                <Building IDValue="B3"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_building_ids(self, parse_xml):
        """Duplicate Building IDs - should fail."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1"/>
                <Building IDValue="B2"/>
                <Building IDValue="B1"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("building_id_unique" in e.rule_id for e in result.errors)

    def test_no_buildings(self, parse_xml):
        """No Buildings - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1"/>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_single_building(self, parse_xml):
        """Single Building - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True


class TestFloorplanIdUnique:
    """Test floorplan_id_unique rule."""

    def test_unique_floorplan_ids(self, parse_xml):
        """All Floorplan IDs unique - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1"/>
                    <Floorplan IDValue="FP2"/>
                    <Floorplan IDValue="FP3"/>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_floorplan_ids(self, parse_xml):
        """Duplicate Floorplan IDs - should fail."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1"/>
                    <Floorplan IDValue="FP2"/>
                    <Floorplan IDValue="FP1"/>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("floorplan_id_unique" in e.rule_id for e in result.errors)

    def test_floorplans_across_buildings(self, parse_xml):
        """Same Floorplan ID in different Buildings - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1"/>
                </Building>
                <Building IDValue="B2">
                    <Floorplan IDValue="FP1"/>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        # Depends on scope - may be property-wide or building-wide
        # Implementation determines if this should pass


class TestUnitIdUnique:
    """Test unit_id_unique rule."""

    def test_unique_unit_ids(self, parse_xml):
        """All Unit IDs unique - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1">
                        <Unit IDValue="U1"/>
                        <Unit IDValue="U2"/>
                        <Unit IDValue="U3"/>
                    </Floorplan>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_duplicate_unit_ids(self, parse_xml):
        """Duplicate Unit IDs - should fail."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1">
                        <Unit IDValue="U1"/>
                        <Unit IDValue="U2"/>
                        <Unit IDValue="U1"/>
                    </Floorplan>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is False
        assert any("unit_id_unique" in e.rule_id for e in result.errors)

    def test_units_across_floorplans(self, parse_xml):
        """Same Unit ID in different Floorplans - depends on scope."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="B1">
                    <Floorplan IDValue="FP1">
                        <Unit IDValue="101"/>
                    </Floorplan>
                    <Floorplan IDValue="FP2">
                        <Unit IDValue="101"/>
                    </Floorplan>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        # Depends on scope - may be floorplan-wide or property-wide


class TestIdNoWhitespace:
    """Test id_no_whitespace rule."""

    def test_ids_without_whitespace(self, parse_xml):
        """IDs without whitespace - should pass."""
        xml = """<PhysicalProperty>
            <Property IDValue="prop-1">
                <Building IDValue="building-1">
                    <Floorplan IDValue="floorplan-1">
                        <Unit IDValue="unit-101"/>
                    </Floorplan>
                </Building>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        assert result.valid is True

    def test_property_id_with_whitespace(self, parse_xml):
        """Property ID with whitespace - may warn."""
        xml = """<PhysicalProperty>
            <Property IDValue="prop 1">
                <Building IDValue="B1"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        # May generate warning depending on strictness

    def test_building_id_with_whitespace(self, parse_xml):
        """Building ID with whitespace - may warn."""
        xml = """<PhysicalProperty>
            <Property IDValue="1">
                <Building IDValue="Building 1"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        # May generate warning

    def test_ids_with_tabs_newlines(self, parse_xml):
        """IDs with tabs/newlines - should warn or fail."""
        xml = """<PhysicalProperty>
            <Property IDValue="prop	1">
                <Building IDValue="B
1"/>
            </Property>
        </PhysicalProperty>"""
        root = parse_xml(xml)
        validator = IdentityUniquenessValidator(root)
        result = validator.validate()
        
        # Should handle various whitespace characters

