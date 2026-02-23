"""Tests for CLI."""

import requests  # type: ignore

def test_requests_import():
    """Test requests import and usage."""
    if requests is None:
        raise ImportError("The 'requests' library is not installed, this test requires it.")
    assert requests is not None

    response = requests.get('https://httpbin.org/get', timeout=10)
    assert response.status_code == 200
