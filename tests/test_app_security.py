"""Tests for Flask app security headers."""

import pytest

flask = pytest.importorskip("flask")
from html2md.app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that all responses include appropriate security headers."""
    response = client.get('/health')

    # Assert successful response
    assert response.status_code == 200

    # Check security headers
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Content-Security-Policy') == "default-src 'none'"
    assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
