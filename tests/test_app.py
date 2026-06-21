"""Tests for the Flask application."""

import pytest

from html2md.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health endpoint returns a successful status."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'ok'
    assert response.json['service'] == 'html2md'
    assert 'version' in response.json


def test_security_headers(client):
    """Test that security headers are applied to responses."""
    response = client.get('/health')
    assert response.headers['X-Content-Type-Options'] == 'nosniff'
    assert response.headers['X-Frame-Options'] == 'DENY'
    assert response.headers['Content-Security-Policy'] == "default-src 'none'"
    assert response.headers['Strict-Transport-Security'] == 'max-age=31536000; includeSubDomains'
