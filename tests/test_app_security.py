import pytest
from html2md.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers(client):
    """Test that all responses include appropriate security headers."""
    response = client.get('/health')

    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert "default-src 'none'" in headers.get('Content-Security-Policy', '')
    assert 'max-age=' in headers.get('Strict-Transport-Security', '')
