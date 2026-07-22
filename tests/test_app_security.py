"""Security tests for the Flask application."""

import pytest

try:
    from html2md.app import app
except ImportError:
    app = None

@pytest.mark.skipif(app is None, reason="Flask is not installed")
def test_security_headers_present():
    """Test that all required security headers are present in the response."""
    app.testing = True
    client = app.test_client()

    response = client.get('/health')

    assert response.status_code == 200

    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('X-XSS-Protection') == '1; mode=block'
    assert headers.get('Content-Security-Policy') == "default-src 'self'"
    assert headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
