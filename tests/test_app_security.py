"""Security tests for the Flask app."""
import pytest

try:
    from html2md.app import app
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

pytestmark = pytest.mark.skipif(not HAS_FLASK, reason="flask is not installed")

@pytest.fixture
def client():
    if not HAS_FLASK:
        pytest.skip("flask is not installed")
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_security_headers_present(client):
    """Test that all responses include appropriate security headers."""
    response = client.get('/health')

    # Assert standard security headers are present
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'
    assert response.headers.get('Content-Security-Policy') == "default-src 'none'"
