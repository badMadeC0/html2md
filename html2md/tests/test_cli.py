"""Tests for CLI."""

import requests  # type: ignore

def test_requests_import():
    """Test requests import and usage."""
    assert requests is not None

    response = requests.get('https://httpbin.org/get', timeout=10)
    assert response.status_code == 200
