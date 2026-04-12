"""Tests for the Flask application."""
import pytest

pytest.importorskip("flask")

from html2md.app import app

@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Test that the health endpoint returns OK."""
    rv = client.get('/health')
    assert rv.status_code == 200
    json_data = rv.get_json()
    assert json_data['status'] == 'ok'
    assert json_data['service'] == 'html2md'

def test_security_headers(client):
    """Test that security headers are set on responses."""
    rv = client.get('/health')
    assert rv.headers.get('X-Content-Type-Options') == 'nosniff'
    assert rv.headers.get('X-Frame-Options') == 'DENY'
    assert rv.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    assert rv.headers.get('Content-Security-Policy') == "default-src 'self'"
