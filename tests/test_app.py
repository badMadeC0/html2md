"""Tests for the Flask application."""

import pytest

flask = pytest.importorskip("flask")

from html2md.app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test that the health endpoint returns 200 OK."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'html2md'

def test_security_headers(client):
    """Test that security headers are set on responses."""
    response = client.get('/health')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert 'max-age=31536000' in response.headers.get('Strict-Transport-Security', '')
    assert "default-src 'none'" in response.headers.get('Content-Security-Policy', '')
