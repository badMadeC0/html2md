"""Security-focused tests for Flask application."""

import pytest
flask = pytest.importorskip("flask")

from html2md.app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Verify that all required security headers are set on responses."""
    response = client.get("/health")
    assert response.status_code == 200

    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert "default-src 'none'" in headers.get("Content-Security-Policy", "")
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
