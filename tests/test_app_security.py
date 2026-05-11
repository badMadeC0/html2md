"""Security tests for Flask app security headers and rate limiting."""

import pytest

try:
    import flask
    from html2md.app import app
except ImportError:
    flask = None


@pytest.mark.skipif(flask is None, reason="Flask not installed")
def test_app_security_headers():
    """Test that all endpoints return the required security headers."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        response = client.get('/health')

        # Verify the response was successful
        assert response.status_code == 200

        # Verify security headers are present
        assert response.headers.get('X-Content-Type-Options') == 'nosniff'
        assert response.headers.get('X-Frame-Options') == 'DENY'
        assert response.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'
        assert response.headers.get('Content-Security-Policy') == "default-src 'self'"
        assert response.headers.get('X-XSS-Protection') == '1; mode=block'


@pytest.fixture
def clear_rate_limit():
    """Clear rate limiting state before and after the test."""
    from html2md.app import ip_requests
    ip_requests.clear()
    yield
    ip_requests.clear()


@pytest.mark.skipif(flask is None, reason="Flask not installed")
def test_app_rate_limiting(clear_rate_limit):
    """Test that the application correctly enforces rate limiting."""
    app.config['TESTING'] = True

    with app.test_client() as client:
        # Send 100 successful requests (the limit)
        for _ in range(100):
            response = client.get('/health')
            assert response.status_code == 200

        # The 101st request should be rate-limited
        response = client.get('/health')
        assert response.status_code == 429
        assert b'Too Many Requests' in response.data
