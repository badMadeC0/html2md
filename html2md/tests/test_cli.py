"""Tests for CLI."""

import requests  # type: ignore

def test_requests_import():
    """Test requests import and usage."""
    if requests is None:
        return
    assert requests is not None

    try:
        response = requests.get('https://httpbin.org/get', timeout=10)
        assert response.status_code == 200
    except requests.RequestException:
        # Ignore network errors in tests
        pass
