"""Tests for the Flask application."""

import pytest

try:
    import flask
    from html2md.app import app
except ImportError:
    flask = None
    app = None

pytestmark = pytest.mark.skipif(flask is None, reason="Flask is not installed")


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test that the health endpoint returns correctly."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["service"] == "html2md"
    assert "version" in data


def test_security_headers(client):
    """Test that security headers are added to responses."""
    response = client.get("/health")
    headers = response.headers

    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "DENY"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert (
        headers.get("Content-Security-Policy")
        == "default-src 'none'; frame-ancestors 'none';"
    )
    assert (
        headers.get("Strict-Transport-Security")
        == "max-age=31536000; includeSubDomains"
    )
