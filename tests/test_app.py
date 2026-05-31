import pytest

try:
    import flask
except ImportError:
    pytest.skip("flask is not installed", allow_module_level=True)

from html2md.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'ok'
    assert data['service'] == 'html2md'

def test_security_headers(client):
    response = client.get('/health')
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('X-XSS-Protection') == '1; mode=block'
    assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
    assert "default-src 'self'" in response.headers.get('Content-Security-Policy', '')
