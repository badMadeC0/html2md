"""Tests for CLI."""

import unittest.mock
import requests  # type: ignore


def test_requests_import():
    """Test requests import and usage."""
    assert requests is not None

    with unittest.mock.patch("requests.get") as mock_get:
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = requests.get("https://httpbin.org/get", timeout=10)
        assert response.status_code == 200
