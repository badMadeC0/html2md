"""Tests for html2md Flask application."""
import pytest
import sys
import os

# Skip tests if flask is not installed
pytest.importorskip("flask")

# Add src to path so we can import our app directly if needed (pytest often does this anyway)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html2md.app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint_has_security_headers(client):
    """Test that the /health endpoint returns expected security headers."""
    response = client.get('/health')

    # Assert successful response
    assert response.status_code == 200

    # Assert security headers are present
    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('Content-Security-Policy') == "default-src 'none'"
    assert headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
