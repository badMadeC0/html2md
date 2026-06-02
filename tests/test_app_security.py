"""Security tests for Flask app."""
import pytest

flask = pytest.importorskip("flask")
from html2md.app import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that security headers are present in responses."""
    response = client.get('/health')
    assert response.status_code == 200
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    assert "default-src 'none'" in response.headers.get('Content-Security-Policy', '')
