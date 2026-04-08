import pytest

flask = pytest.importorskip("flask")

from html2md.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Test that all required security headers are included in the response."""
    response = client.get('/health')
    assert response.status_code == 200

    headers = response.headers
    assert headers.get('X-Content-Type-Options') == 'nosniff'
    assert headers.get('X-Frame-Options') == 'DENY'
    assert headers.get('Content-Security-Policy') == "default-src 'none'"
    assert headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'html2md'
