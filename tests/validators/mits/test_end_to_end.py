"""
End-to-end integration tests using complete XML documents.

Tests the full validation pipeline with real-world XML files.
"""

import pytest
from pathlib import Path

from app.validators.mits import validate_mits_document


class TestFullXML:
    """End-to-end tests using test_full.xml."""
    
    @pytest.fixture
    def full_xml(self):
        """Load test_full.xml file."""
        xml_path = Path(__file__).parent.parent.parent / "test_full.xml"
        assert xml_path.exists(), f"test_full.xml not found at {xml_path}"
        return xml_path.read_text(encoding="utf-8")
    
    def test_full_xml_loads(self, full_xml):
        """test_full.xml should load and be parseable."""
        assert full_xml is not None
        assert len(full_xml) > 0
        assert "<?xml" in full_xml
        assert "<PhysicalProperty>" in full_xml
    
    def test_full_xml_validation(self, full_xml):
        """test_full.xml should go through complete validation pipeline."""
        result = validate_mits_document(full_xml)
        
        # Result should have expected structure
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "info" in result
        
        # Log results for analysis
        print(f"\n=== FULL XML VALIDATION RESULTS ===")
        print(f"Valid: {result['valid']}")
        print(f"Errors: {len(result['errors'])}")
        print(f"Warnings: {len(result['warnings'])}")
        print(f"Info: {len(result['info'])}")
        
        if result['errors']:
            print("\nErrors found:")
            for error in result['errors'][:10]:  # First 10 errors
                print(f"  - {error}")
        
        if result['warnings']:
            print("\nWarnings found:")
            for warning in result['warnings'][:5]:  # First 5 warnings
                print(f"  - {warning}")
    
    def test_full_xml_xml_structure_rules(self, full_xml):
        """test_full.xml should pass XML structure validation."""
        result = validate_mits_document(full_xml)
        
        # Should not have basic XML structure errors
        xml_structure_errors = [
            e for e in result['errors'] 
            if any(rule in e for rule in [
                'xml_wellformed',
                'xml_encoding_utf8',
                'root_is_physical_property',
                'property_exists'
            ])
        ]
        
        if xml_structure_errors:
            print("\nXML Structure errors:")
            for error in xml_structure_errors:
                print(f"  - {error}")
        
        # Basic structure should be valid
        assert not any('xml_wellformed' in e for e in result['errors']), \
            "XML should be well-formed"
        assert not any('root_is_physical_property' in e for e in result['errors']), \
            "Root should be PhysicalProperty"
    
    def test_full_xml_property_count(self, full_xml):
        """Count properties in test_full.xml."""
        from defusedxml import ElementTree as ET
        root = ET.fromstring(full_xml.encode('utf-8'))
        properties = root.findall('Property')
        
        print(f"\n=== FULL XML STRUCTURE ===")
        print(f"Properties: {len(properties)}")
        
        for idx, prop in enumerate(properties, 1):
            prop_id = prop.get('IDValue', 'NO_ID')
            buildings = prop.findall('.//Building')
            floorplans = prop.findall('.//Floorplan')
            units = prop.findall('.//Unit')
            charge_classes = prop.findall('.//ChargeOfferClass')
            charge_items = prop.findall('.//ChargeOfferItem')
            
            print(f"\nProperty {idx} (ID: {prop_id}):")
            print(f"  Buildings: {len(buildings)}")
            print(f"  Floorplans: {len(floorplans)}")
            print(f"  Units: {len(units)}")
            print(f"  ChargeOfferClass: {len(charge_classes)}")
            print(f"  ChargeOfferItem: {len(charge_items)}")
        
        assert len(properties) > 0, "Should have at least one property"
    
    def test_full_xml_validation_categories(self, full_xml):
        """Categorize validation results from test_full.xml."""
        result = validate_mits_document(full_xml)
        
        # Categorize errors by validator type
        categories = {
            'xml_structure': [],
            'fee_hierarchy': [],
            'identity': [],
            'charge_class': [],
            'class_limits': [],
            'offer_item': [],
            'characteristics': [],
            'amount_basis': [],
            'amount_format': [],
            'frequency': [],
            'specialized_items': [],
            'cross_validation': [],
            'data_quality': [],
            'other': []
        }
        
        for error in result['errors']:
            categorized = False
            
            if any(x in error for x in ['xml_', 'root_', 'property_']):
                categories['xml_structure'].append(error)
                categorized = True
            elif any(x in error for x in ['fee_', 'class_item_amount']):
                categories['fee_hierarchy'].append(error)
                categorized = True
            elif any(x in error for x in ['building_id', 'floorplan_id', 'unit_id', 'id_no_whitespace']):
                categories['identity'].append(error)
                categorized = True
            elif any(x in error for x in ['class_has', 'class_code', 'class_no_empty', 'class_limits']):
                categories['charge_class'].append(error)
                categorized = True
            elif any(x in error for x in ['limit_']):
                categories['class_limits'].append(error)
                categorized = True
            elif any(x in error for x in ['item_has', 'item_internal', 'item_no_duplicate', 'item_occurrence', 'item_amount', 'item_percentage', 'item_pms']):
                categories['offer_item'].append(error)
                categorized = True
            elif any(x in error for x in ['char_']):
                categories['characteristics'].append(error)
                categorized = True
            elif any(x in error for x in ['basis_']):
                categories['amount_basis'].append(error)
                categorized = True
            elif any(x in error for x in ['amount_', 'percentage_', 'term_', 'date_', 'scheduled_', 'duration_']):
                categories['amount_format'].append(error)
                categorized = True
            elif any(x in error for x in ['frequency_', 'onetime_', 'amount_per']):
                categories['frequency'].append(error)
                categorized = True
            elif any(x in error for x in ['pet_', 'parking_', 'storage_']):
                categories['specialized_items'].append(error)
                categorized = True
            elif any(x in error for x in ['reference_', 'internal_code_unique', 'cross_level', 'included_']):
                categories['cross_validation'].append(error)
                categorized = True
            elif any(x in error for x in ['text_', 'numeric_', 'name_unique']):
                categories['data_quality'].append(error)
                categorized = True
            
            if not categorized:
                categories['other'].append(error)
        
        print(f"\n=== VALIDATION ERROR CATEGORIES ===")
        for category, errors in categories.items():
            if errors:
                print(f"\n{category.upper().replace('_', ' ')} ({len(errors)} errors):")
                for error in errors[:3]:  # Show first 3 of each category
                    print(f"  - {error}")
                if len(errors) > 3:
                    print(f"  ... and {len(errors) - 3} more")


class TestPartialXML:
    """End-to-end tests using test_partial.xml."""
    
    @pytest.fixture
    def partial_xml(self):
        """Load test_partial.xml file."""
        xml_path = Path(__file__).parent.parent.parent / "test_partial.xml"
        if not xml_path.exists():
            pytest.skip(f"test_partial.xml not found at {xml_path}")
        return xml_path.read_text(encoding="utf-8")
    
    def test_partial_xml_loads(self, partial_xml):
        """test_partial.xml should load and be parseable."""
        assert partial_xml is not None
        assert len(partial_xml) > 0
        assert "<?xml" in partial_xml
        assert "<PhysicalProperty>" in partial_xml
    
    def test_partial_xml_validation(self, partial_xml):
        """test_partial.xml should go through complete validation pipeline."""
        result = validate_mits_document(partial_xml)
        
        # Result should have expected structure
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "info" in result
        
        print(f"\n=== PARTIAL XML VALIDATION RESULTS ===")
        print(f"Valid: {result['valid']}")
        print(f"Errors: {len(result['errors'])}")
        print(f"Warnings: {len(result['warnings'])}")
        print(f"Info: {len(result['info'])}")
        
        if result['errors']:
            print("\nErrors found:")
            for error in result['errors'][:10]:
                print(f"  - {error}")
    
    def test_partial_xml_structure(self, partial_xml):
        """Analyze structure of test_partial.xml."""
        from defusedxml import ElementTree as ET
        root = ET.fromstring(partial_xml.encode('utf-8'))
        properties = root.findall('Property')
        
        print(f"\n=== PARTIAL XML STRUCTURE ===")
        print(f"Properties: {len(properties)}")
        
        for idx, prop in enumerate(properties, 1):
            prop_id = prop.get('IDValue', 'NO_ID')
            charge_items = prop.findall('.//ChargeOfferItem')
            pet_items = prop.findall('.//PetOfferItem')
            parking_items = prop.findall('.//ParkingOfferItem')
            storage_items = prop.findall('.//StorageOfferItem')
            
            print(f"\nProperty {idx} (ID: {prop_id}):")
            print(f"  ChargeOfferItem: {len(charge_items)}")
            print(f"  PetOfferItem: {len(pet_items)}")
            print(f"  ParkingOfferItem: {len(parking_items)}")
            print(f"  StorageOfferItem: {len(storage_items)}")
        
        assert len(properties) > 0, "Should have at least one property"


class TestEndToEndScenarios:
    """Additional end-to-end test scenarios."""
    
    def test_minimal_valid_document(self):
        """Test with minimal valid MITS document."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="prop-1">
        <ChargeOfferClass Code="APP">
            <ChargeOfferItem InternalCode="app_fee">
                <Name>Application Fee</Name>
                <Description>One-time application fee</Description>
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                    <Lifecycle>At Application</Lifecycle>
                    <PaymentFrequency>One-time</PaymentFrequency>
                </Characteristics>
                <AmountBasis>Explicit</AmountBasis>
                <ChargeOfferAmount>
                    <Amounts>50.00</Amounts>
                    <Percentage></Percentage>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>"""
        
        result = validate_mits_document(xml)
        
        assert result['valid'] is True, f"Minimal document should be valid. Errors: {result['errors']}"
        assert len(result['errors']) == 0
    
    def test_multiple_properties(self):
        """Test document with multiple properties."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="prop-1">
        <ChargeOfferClass Code="APP">
            <ChargeOfferItem InternalCode="fee1">
                <Name>Fee 1</Name>
                <Description>Test</Description>
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                    <Lifecycle>At Application</Lifecycle>
                    <PaymentFrequency>One-time</PaymentFrequency>
                </Characteristics>
                <AmountBasis>Explicit</AmountBasis>
                <ChargeOfferAmount>
                    <Amounts>50.00</Amounts>
                    <Percentage></Percentage>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
    <Property IDValue="prop-2">
        <ChargeOfferClass Code="SEC">
            <ChargeOfferItem InternalCode="fee2">
                <Name>Fee 2</Name>
                <Description>Test</Description>
                <Characteristics>
                    <ChargeRequirement>Mandatory</ChargeRequirement>
                    <Lifecycle>At Application</Lifecycle>
                    <PaymentFrequency>One-time</PaymentFrequency>
                </Characteristics>
                <AmountBasis>Explicit</AmountBasis>
                <ChargeOfferAmount>
                    <Amounts>100.00</Amounts>
                    <Percentage></Percentage>
                </ChargeOfferAmount>
            </ChargeOfferItem>
        </ChargeOfferClass>
    </Property>
</PhysicalProperty>"""
        
        result = validate_mits_document(xml)
        
        # Should handle multiple properties correctly
        assert 'property_id_unique' not in str(result['errors'])
    
    def test_validation_stops_on_critical_errors(self):
        """Test that validation stops early on critical XML errors."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<WrongRoot>
    <Property IDValue="1"/>
</WrongRoot>"""
        
        result = validate_mits_document(xml)
        
        assert result['valid'] is False
        assert any('root_is_physical_property' in e for e in result['errors'])
    
    def test_complex_hierarchy(self):
        """Test document with Building/Floorplan/Unit hierarchy."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
    <Property IDValue="prop-1">
        <Building IDValue="B1">
            <Floorplan IDValue="FP1">
                <Unit IDValue="U101">
                    <ChargeOfferClass Code="RENT">
                        <ChargeOfferItem InternalCode="rent">
                            <Name>Monthly Rent</Name>
                            <Description>Base rent</Description>
                            <Characteristics>
                                <ChargeRequirement>Mandatory</ChargeRequirement>
                                <Lifecycle>During Tenancy</Lifecycle>
                                <PaymentFrequency>Monthly</PaymentFrequency>
                            </Characteristics>
                            <AmountBasis>Explicit</AmountBasis>
                            <ChargeOfferAmount>
                                <Amounts>1500.00</Amounts>
                                <Percentage></Percentage>
                            </ChargeOfferAmount>
                        </ChargeOfferItem>
                    </ChargeOfferClass>
                </Unit>
            </Floorplan>
        </Building>
    </Property>
</PhysicalProperty>"""
        
        result = validate_mits_document(xml)
        
        # Should handle hierarchy correctly
        if not result['valid']:
            print(f"\nHierarchy validation errors: {result['errors']}")

