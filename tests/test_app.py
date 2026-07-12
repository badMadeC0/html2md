"""Tests for the Flask application and security headers."""

import pytest

try:
    import flask
    from html2md.app import app
except ImportError:
    pytest.skip("Flask is not installed", allow_module_level=True)


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test that the health endpoint returns a successful status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_security_headers(client):
    """Test that security headers are injected into responses."""
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-XSS-Protection") == "1; mode=block"
    assert (
        response.headers.get("Strict-Transport-Security")
        == "max-age=31536000; includeSubDomains"
    )
    assert response.headers.get("Server") == "html2md"
    assert response.headers.get("Content-Security-Policy") == "default-src 'self'"
