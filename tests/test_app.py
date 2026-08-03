"""Tests for Flask app."""

import pytest

try:
    import flask
    from html2md.app import app
except ImportError:
    pytest.skip("flask is not installed", allow_module_level=True)


@pytest.fixture
def client():
    """Create a test client for the app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test health endpoint returns 200 OK and expected JSON."""
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'html2md'
    assert 'version' in data


def test_security_headers(client):
    """Test security headers are injected into the response."""
    response = client.get('/health')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    assert response.headers.get('Content-Security-Policy') == "default-src 'self'"
