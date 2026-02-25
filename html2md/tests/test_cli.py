"""Tests for CLI."""

import pytest


def test_requests_import():
    """Test requests import and usage."""
    requests = pytest.importorskip("requests")
    assert requests is not None

    try:
        response = requests.get("https://httpbin.org/get", timeout=10)
        assert response.status_code == 200
    except requests.exceptions.RequestException:
        pytest.skip("Network unavailable")
