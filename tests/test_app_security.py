import pytest

flask = pytest.importorskip("flask")

from html2md.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Test that all responses include the expected security headers."""
    response = client.get('/health')

    assert response.status_code == 200
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Content-Security-Policy') == "default-src 'none'"
