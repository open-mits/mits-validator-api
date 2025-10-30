"""Tests for validation API endpoint."""

import pytest
from fastapi import status


class TestValidationEndpoint:
    """Test suite for POST /v5.0/validate endpoint."""

    def test_validate_raw_xml_valid(self, client, mits_xml):
        """Test validation with raw XML body (valid MITS document)."""
        response = client.post(
            "/v5.0/validate",
            content=mits_xml["minimal_valid"],
            headers={"Content-Type": "application/xml"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True
        assert len(data["errors"]) == 0
        assert "X-Request-ID" in response.headers

    def test_validate_raw_xml_invalid(self, client, invalid_xml):
        """Test validation with raw XML body (invalid)."""
        response = client.post(
            "/v5.0/validate",
            content=invalid_xml["unclosed_tag"],
            headers={"Content-Type": "application/xml"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_json_wrapped_valid(self, client):
        """Test that JSON-wrapped XML is no longer supported."""
        response = client.post(
            "/v5.0/validate",
            json={"xml": "<root/>"},
            headers={"Content-Type": "application/json"},
        )

        # JSON is no longer accepted, should return validation error
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("Content-Type" in err for err in data["errors"])

    def test_validate_json_wrapped_invalid(self, client, invalid_xml):
        """Test validation with JSON-wrapped XML (invalid)."""
        response = client.post(
            "/v5.0/validate",
            json={"xml": invalid_xml["bad_nesting"]},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_text_xml_content_type(self, client, mits_xml):
        """Test validation with text/xml content type."""
        response = client.post(
            "/v5.0/validate",
            content=mits_xml["minimal_valid"],
            headers={"Content-Type": "text/xml"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True

    def test_validate_invalid_content_type(self, client, valid_xml):
        """Test rejection of invalid content type."""
        response = client.post(
            "/v5.0/validate",
            content=valid_xml["simple"],
            headers={"Content-Type": "text/plain"},
        )

        # Now returns 200 with validation error instead of 400
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("Content-Type" in err for err in data["errors"])

    def test_validate_empty_body(self, client):
        """Test rejection of empty body."""
        response = client.post(
            "/v5.0/validate",
            content="",
            headers={"Content-Type": "application/xml"},
        )

        # Now returns 200 with validation error instead of 400
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("empty" in err.lower() for err in data["errors"])

    def test_validate_json_missing_xml_field(self, client):
        """Test rejection of JSON without 'xml' field."""
        response = client.post(
            "/v5.0/validate",
            json={"data": "<root/>"},
            headers={"Content-Type": "application/json"},
        )

        # JSON no longer supported, returns 200 with validation error
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("Content-Type" in err for err in data["errors"])

    def test_validate_json_empty_xml_field(self, client):
        """Test rejection of JSON with empty 'xml' field."""
        response = client.post(
            "/v5.0/validate",
            json={"xml": ""},
            headers={"Content-Type": "application/json"},
        )

        # JSON no longer supported, returns 200 with validation error
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("Content-Type" in err for err in data["errors"])

    def test_validate_invalid_utf8(self, client):
        """Test rejection of invalid UTF-8 encoding."""
        response = client.post(
            "/v5.0/validate",
            content=b"\xff\xfe<root/>",  # Invalid UTF-8
            headers={"Content-Type": "application/xml"},
        )

        # Now returns 200 with validation error instead of 400
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is False
        assert any("UTF-8" in err or "encoding" in err.lower() for err in data["errors"])

    def test_validate_xxe_protection(self, client, xxe_payloads):
        """Test that XXE attacks are properly blocked."""
        for payload in xxe_payloads:
            response = client.post(
                "/v5.0/validate",
                content=payload,
                headers={"Content-Type": "application/xml"},
            )

            # Should return 200 with valid=False (blocked by validator)
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["valid"] is False

    def test_validate_oversized_body(self, client):
        """Test rejection of oversized request body."""
        # Create XML larger than 512KB limit
        large_xml = "<root>" + ("x" * 600_000) + "</root>"

        # The middleware raises BodyTooLargeError which is an HTTPException
        # In test client, this causes a proper exception
        try:
            response = client.post(
                "/v5.0/validate",
                content=large_xml,
                headers={"Content-Type": "application/xml"},
            )
            # If we somehow get here, check it was rejected
            assert response.status_code == status.HTTP_413_CONTENT_TOO_LARGE
        except Exception as e:
            # Middleware correctly raised BodyTooLargeError
            assert "413" in str(e) or "too large" in str(e).lower()

    def test_validate_complex_valid_xml(self, client, mits_xml):
        """Test validation with complex MITS XML structure."""
        response = client.post(
            "/v5.0/validate",
            content=mits_xml["with_class"],
            headers={"Content-Type": "application/xml"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["valid"] is True

    def test_response_structure(self, client, valid_xml):
        """Test that response has correct structure."""
        response = client.post(
            "/v5.0/validate",
            content=valid_xml["simple"],
            headers={"Content-Type": "application/xml"},
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify all required fields are present
        assert "valid" in data
        assert "errors" in data
        assert "warnings" in data
        assert "info" in data

        # Verify types
        assert isinstance(data["valid"], bool)
        assert isinstance(data["errors"], list)
        assert isinstance(data["warnings"], list)
        assert isinstance(data["info"], list)

    def test_request_id_header(self, client, valid_xml):
        """Test that X-Request-ID header is present in response."""
        response = client.post(
            "/v5.0/validate",
            content=valid_xml["simple"],
            headers={"Content-Type": "application/xml"},
        )

        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        assert len(request_id) > 0


class TestHealthEndpoint:
    """Test suite for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint returns healthy status."""
        response = client.get("/healthz")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestRootEndpoint:
    """Test suite for root endpoint."""

    def test_root_endpoint(self, client):
        """Test root endpoint returns welcome message."""
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
        assert "version" in data


class TestRateLimiting:
    """Test suite for rate limiting functionality."""

    def test_rate_limit_not_exceeded(self, client, valid_xml):
        """Test that normal usage doesn't trigger rate limit."""
        # Make a few requests (well under limit)
        for _ in range(5):
            response = client.post(
                "/v5.0/validate",
                content=valid_xml["simple"],
                headers={"Content-Type": "application/xml"},
            )
            assert response.status_code == status.HTTP_200_OK

    @pytest.mark.skip(reason="Rate limiting test requires actual delays; slow to run")
    def test_rate_limit_exceeded(self, client, valid_xml):
        """Test that excessive requests trigger rate limit."""
        # This test is skipped by default as it requires making 60+ requests
        # and waiting for rate limit to trigger
        responses = []
        for _ in range(65):  # Exceed 60/minute limit
            response = client.post(
                "/v5.0/validate",
                content=valid_xml["simple"],
                headers={"Content-Type": "application/xml"},
            )
            responses.append(response.status_code)

        # At least one request should be rate limited
        assert status.HTTP_429_TOO_MANY_REQUESTS in responses


class TestDocumentation:
    """Test suite for API documentation."""

    def test_openapi_schema_available(self, client):
        """Test that OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == status.HTTP_200_OK

        schema = response.json()
        assert "openapi" in schema
        assert "paths" in schema
        assert "/v5.0/validate" in schema["paths"]

    def test_docs_available(self, client):
        """Test that Swagger UI docs are accessible."""
        response = client.get("/docs")
        assert response.status_code == status.HTTP_200_OK

    def test_redoc_available(self, client):
        """Test that ReDoc documentation is accessible."""
        response = client.get("/redoc")
        assert response.status_code == status.HTTP_200_OK
