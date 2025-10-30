"""Tests for validation service."""

from app.services.validation_service import validate


class TestValidationService:
    """Test suite for validation service orchestration."""

    def test_validate_simple_valid_xml(self, mits_xml):
        """Test validation service with simple valid MITS XML."""
        result = validate(mits_xml["minimal_valid"])

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_complex_valid_xml(self, mits_xml):
        """Test validation service with complex valid MITS XML."""
        result = validate(mits_xml["with_class"])

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_invalid_xml(self, invalid_xml):
        """Test validation service with invalid XML."""
        result = validate(invalid_xml["unclosed_tag"])

        assert result["valid"] is False
        assert len(result["errors"]) > 0
        # Error message changed to be more specific
        assert any("xml" in err.lower() for err in result["errors"])

    def test_validate_empty_string(self, invalid_xml):
        """Test validation service with empty string."""
        result = validate(invalid_xml["empty"])

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_with_bom(self, mits_xml):
        """Test validation service strips UTF-8 BOM."""
        xml_with_bom = "\ufeff" + mits_xml["minimal_valid"]
        result = validate(xml_with_bom)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_with_whitespace(self, mits_xml):
        """Test validation service handles leading/trailing whitespace."""
        xml_with_whitespace = "  \n  " + mits_xml["minimal_valid"] + "  \n  "
        result = validate(xml_with_whitespace)

        assert result["valid"] is True
        assert len(result["errors"]) == 0

    def test_validate_with_illegal_characters(self):
        """Test validation service rejects illegal XML characters."""
        # Control character \x00 is illegal in XML 1.0
        xml_with_illegal = "<root>\x00illegal</root>"
        result = validate(xml_with_illegal)

        assert result["valid"] is False
        assert any("illegal" in error.lower() for error in result["errors"])

    def test_validate_xxe_attempts(self, xxe_payloads):
        """Test validation service blocks XXE attacks."""
        for payload in xxe_payloads:
            result = validate(payload)
            assert result["valid"] is False
            assert len(result["errors"]) > 0

    def test_validate_response_structure(self, valid_xml):
        """Test that response has correct structure."""
        result = validate(valid_xml["simple"])

        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result
        assert "info" in result

        assert isinstance(result["valid"], bool)
        assert isinstance(result["errors"], list)
        assert isinstance(result["warnings"], list)
        assert isinstance(result["info"], list)

    def test_validate_whitespace_only(self, invalid_xml):
        """Test validation with whitespace-only content."""
        result = validate(invalid_xml["whitespace_only"])

        assert result["valid"] is False
        assert len(result["errors"]) > 0
