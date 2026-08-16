"""Tests for Flask app security headers."""

import pytest

pytest.importorskip("flask")

from html2md.app import app


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_security_headers_present(client):
    """Test that all responses include required security headers."""
    response = client.get('/health')
    assert response.status_code == 200

    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('Content-Security-Policy') == "default-src 'none'; frame-ancestors 'none'"
    assert headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
