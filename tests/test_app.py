"""Tests for the Flask application."""

import pytest

try:
    from html2md.app import app
except ImportError:
    app = None


@pytest.mark.skipif(app is None, reason="Flask is not installed")
def test_health_endpoint():
    """Test the /health endpoint returns correct JSON and security headers."""
    client = app.test_client()
    response = client.get('/health')

    # Check status code
    assert response.status_code == 200

    # Check JSON body
    data = response.get_json()
    assert data is not None
    assert data.get('status') == 'ok'
    assert data.get('service') == 'html2md'
    assert 'version' in data

@pytest.mark.skipif(app is None, reason="Flask is not installed")
def test_security_headers():
    """Test that security headers are applied to responses."""
    client = app.test_client()
    response = client.get('/health')

    # Check security headers
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    assert response.headers.get('Content-Security-Policy') == "default-src 'none'"
