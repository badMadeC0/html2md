"""Security tests for the Flask application."""

import pytest
from html2md.app import app

@pytest.fixture
def client():
    """Test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Test that all responses contain the required security headers."""
    response = client.get('/health')
    assert response.status_code == 200

    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('Content-Security-Policy') == "default-src 'none'"
