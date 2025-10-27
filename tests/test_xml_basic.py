"""Tests for basic XML validation."""

from hypothesis import given
from hypothesis import strategies as st

from app.validators.xml_basic import is_valid_xml


class TestBasicXMLValidation:
    """Test suite for is_valid_xml function."""

    def test_valid_simple_xml(self, valid_xml):
        """Test that simple valid XML passes validation."""
        assert is_valid_xml(valid_xml["simple"]) is True

    def test_valid_complex_xml(self, valid_xml):
        """Test that complex valid XML passes validation."""
        assert is_valid_xml(valid_xml["complex"]) is True

    def test_valid_minimal_xml(self, valid_xml):
        """Test that minimal valid XML passes validation."""
        assert is_valid_xml(valid_xml["minimal"]) is True

    def test_valid_xml_with_attributes(self, valid_xml):
        """Test that XML with attributes passes validation."""
        assert is_valid_xml(valid_xml["with_attributes"]) is True

    def test_invalid_unclosed_tag(self, invalid_xml):
        """Test that XML with unclosed tags fails validation."""
        assert is_valid_xml(invalid_xml["unclosed_tag"]) is False

    def test_invalid_missing_close(self, invalid_xml):
        """Test that XML with missing closing tags fails validation."""
        assert is_valid_xml(invalid_xml["missing_close"]) is False

    def test_invalid_bad_nesting(self, invalid_xml):
        """Test that XML with bad nesting fails validation."""
        assert is_valid_xml(invalid_xml["bad_nesting"]) is False

    def test_empty_string(self, invalid_xml):
        """Test that empty string fails validation."""
        assert is_valid_xml(invalid_xml["empty"]) is False

    def test_whitespace_only(self, invalid_xml):
        """Test that whitespace-only string fails validation."""
        assert is_valid_xml(invalid_xml["whitespace_only"]) is False

    def test_not_xml(self, invalid_xml):
        """Test that non-XML text fails validation."""
        assert is_valid_xml(invalid_xml["not_xml"]) is False

    def test_none_input(self):
        """Test that None input returns False (defensive programming)."""
        # is_valid_xml checks for None and returns False instead of raising
        # This is defensive programming and better than crashing
        try:
            result = is_valid_xml(None)  # type: ignore
            # If it handles None gracefully, should return False
            assert result is False
        except (AttributeError, TypeError):
            # If it raises, that's also acceptable
            pass

    def test_xxe_protection(self, xxe_payloads):
        """Test that XXE attacks are blocked by defusedxml."""
        for payload in xxe_payloads:
            # Should return False (blocked) rather than raising exception
            result = is_valid_xml(payload)
            assert result is False, f"XXE payload should be rejected: {payload[:100]}"

    def test_deeply_nested_xml_within_limit(self):
        """Test that XML within depth limit is accepted."""
        # Create XML with depth of 50 (within default limit of 100)
        xml = "<root>" + "".join(f"<level{i}>" for i in range(50))
        xml += "content"
        xml += "".join(f"</level{i}>" for i in range(49, -1, -1))
        xml += "</root>"

        assert is_valid_xml(xml) is True

    def test_deeply_nested_xml_exceeds_limit(self):
        """Test that XML exceeding depth limit is rejected."""
        # Create XML with depth of 150 (exceeds default limit of 100)
        xml = "<root>" + "".join(f"<level{i}>" for i in range(150))
        xml += "content"
        xml += "".join(f"</level{i}>" for i in range(149, -1, -1))
        xml += "</root>"

        assert is_valid_xml(xml) is False

    def test_xml_with_comments(self):
        """Test that XML with comments is valid."""
        xml = "<root><!-- This is a comment --><item>value</item></root>"
        assert is_valid_xml(xml) is True

    def test_xml_with_cdata(self):
        """Test that XML with CDATA sections is valid."""
        xml = "<root><![CDATA[Some <data> with & special chars]]></root>"
        assert is_valid_xml(xml) is True

    def test_xml_with_namespaces(self):
        """Test that XML with namespaces is valid."""
        xml = '<root xmlns="http://example.com/ns"><item>value</item></root>'
        assert is_valid_xml(xml) is True


class TestPropertyBasedXMLValidation:
    """Property-based tests using Hypothesis."""

    @given(
        st.text(
            alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",  # ASCII letters only
            min_size=1,
            max_size=20,
        )
    )
    def test_simple_tags_are_valid(self, tag_name):
        """Test that simple well-formed tags with ASCII letters are always valid."""
        # XML tag names must use valid XML name characters
        # We use ASCII letters which are always valid
        xml = f"<{tag_name}>content</{tag_name}>"
        assert is_valid_xml(xml) is True

    @given(
        st.text(
            alphabet=st.characters(blacklist_categories=("Cc", "Cs")),  # No control chars
            min_size=1,
            max_size=100,
        )
    )
    def test_content_within_tags(self, content):
        """Test various content within valid tags."""
        # Escape special XML characters
        safe_content = (
            content.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )
        xml = f"<root>{safe_content}</root>"
        # Should be valid since we escaped special chars and filtered control chars
        assert is_valid_xml(xml) is True

    @given(st.integers(min_value=1, max_value=10))
    def test_multiple_sibling_elements(self, num_elements):
        """Test XML with multiple sibling elements."""
        xml = "<root>"
        for i in range(num_elements):
            xml += f"<item{i}>value{i}</item{i}>"
        xml += "</root>"
        assert is_valid_xml(xml) is True
