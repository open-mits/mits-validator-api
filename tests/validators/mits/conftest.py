"""
Shared fixtures for MITS validator tests.
"""

import pytest
from xml.etree.ElementTree import Element, SubElement
from defusedxml import ElementTree as ET


@pytest.fixture
def minimal_valid_property():
    """Create a minimal valid Property element."""
    return """<Property IDValue="prop-1">
    <ChargeOfferClass Code="APP">
        <ChargeOfferItem InternalCode="fee1">
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
</Property>"""


@pytest.fixture
def parse_xml():
    """Helper function to parse XML strings."""
    def _parse(xml_string: str) -> Element:
        if not xml_string.strip().startswith("<?xml"):
            xml_string = f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_string}'
        return ET.fromstring(xml_string.encode("utf-8"))
    return _parse


@pytest.fixture
def create_physical_property():
    """Helper to create PhysicalProperty wrapper."""
    def _create(content: str) -> str:
        return f"""<?xml version="1.0" encoding="UTF-8"?>
<PhysicalProperty>
{content}
</PhysicalProperty>"""
    return _create


@pytest.fixture
def create_property():
    """Helper to create Property element."""
    def _create(id_value: str = "1", content: str = "") -> str:
        return f'<Property IDValue="{id_value}">{content}</Property>'
    return _create


@pytest.fixture
def create_charge_class():
    """Helper to create ChargeOfferClass element."""
    def _create(code: str = "APP", content: str = "") -> str:
        return f'<ChargeOfferClass Code="{code}">{content}</ChargeOfferClass>'
    return _create


@pytest.fixture
def create_charge_item():
    """Helper to create ChargeOfferItem element."""
    def _create(
        internal_code: str = "item1",
        name: str = "Test Item",
        description: str = "Test Description",
        requirement: str = "Mandatory",
        lifecycle: str = "At Application",
        amount_basis: str = "Explicit",
        amounts: str = "50.00",
        frequency: str = "One-time",
        extra_content: str = "",
    ) -> str:
        return f"""<ChargeOfferItem InternalCode="{internal_code}">
    <Name>{name}</Name>
    <Description>{description}</Description>
    <Characteristics>
        <ChargeRequirement>{requirement}</ChargeRequirement>
        <Lifecycle>{lifecycle}</Lifecycle>
        <PaymentFrequency>{frequency}</PaymentFrequency>
    </Characteristics>
    <AmountBasis>{amount_basis}</AmountBasis>
    <ChargeOfferAmount>
        <Amounts>{amounts}</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
    {extra_content}
</ChargeOfferItem>"""
    return _create


@pytest.fixture
def create_pet_item():
    """Helper to create PetOfferItem element."""
    def _create(
        internal_code: str = "pet1",
        name: str = "Pet Fee",
        description: str = "Pet deposit",
        pet_allowed: str = "Yes",
        extra_content: str = "",
    ) -> str:
        return f"""<PetOfferItem InternalCode="{internal_code}">
    <Name>{name}</Name>
    <Description>{description}</Description>
    <PetAllowed>{pet_allowed}</PetAllowed>
    <Characteristics>
        <ChargeRequirement>Conditional</ChargeRequirement>
        <Lifecycle>At Move-In</Lifecycle>
    </Characteristics>
    <AmountBasis>Explicit</AmountBasis>
    <ChargeOfferAmount>
        <Amounts>200.00</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
    {extra_content}
</PetOfferItem>"""
    return _create


@pytest.fixture
def create_parking_item():
    """Helper to create ParkingOfferItem element."""
    def _create(
        internal_code: str = "parking1",
        name: str = "Parking Fee",
        description: str = "Monthly parking",
        extra_content: str = "",
    ) -> str:
        return f"""<ParkingOfferItem InternalCode="{internal_code}">
    <Name>{name}</Name>
    <Description>{description}</Description>
    <Characteristics>
        <ChargeRequirement>Optional</ChargeRequirement>
        <Lifecycle>During Tenancy</Lifecycle>
        <PaymentFrequency>Monthly</PaymentFrequency>
    </Characteristics>
    <AmountBasis>Explicit</AmountBasis>
    <ChargeOfferAmount>
        <Amounts>50.00</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
    {extra_content}
</ParkingOfferItem>"""
    return _create


@pytest.fixture
def create_storage_item():
    """Helper to create StorageOfferItem element."""
    def _create(
        internal_code: str = "storage1",
        name: str = "Storage Unit",
        description: str = "Climate controlled storage",
        extra_content: str = "",
    ) -> str:
        return f"""<StorageOfferItem InternalCode="{internal_code}">
    <Name>{name}</Name>
    <Description>{description}</Description>
    <Characteristics>
        <ChargeRequirement>Optional</ChargeRequirement>
        <Lifecycle>During Tenancy</Lifecycle>
        <PaymentFrequency>Monthly</PaymentFrequency>
    </Characteristics>
    <AmountBasis>Explicit</AmountBasis>
    <ChargeOfferAmount>
        <Amounts>25.00</Amounts>
        <Percentage></Percentage>
    </ChargeOfferAmount>
    {extra_content}
</StorageOfferItem>"""
    return _create


@pytest.fixture
def assert_has_error():
    """Helper to assert a result contains a specific error rule."""
    def _assert(result: dict, rule_id: str, message_contains: str = None):
        errors = result.get("errors", [])
        matching_errors = [e for e in errors if f"[{rule_id}]" in e]
        
        assert len(matching_errors) > 0, f"Expected error with rule_id '{rule_id}', but found errors: {errors}"
        
        if message_contains:
            assert any(message_contains in e for e in matching_errors), \
                f"Expected error to contain '{message_contains}', but got: {matching_errors}"
        
        return matching_errors[0]
    return _assert


@pytest.fixture
def assert_no_errors():
    """Helper to assert a result has no errors."""
    def _assert(result: dict):
        errors = result.get("errors", [])
        assert len(errors) == 0, f"Expected no errors, but found: {errors}"
        assert result.get("valid") is True, "Expected valid=True"
    return _assert

