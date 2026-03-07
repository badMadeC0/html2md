"""Tests for CLI."""

import requests  # type: ignore
from unittest.mock import patch, Mock

def test_requests_import():
    """Test requests import and usage without real network calls."""
    assert requests is not None

    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        response = requests.get('https://httpbin.org/get', timeout=10)
        assert response.status_code == 200
        mock_get.assert_called_once_with('https://httpbin.org/get', timeout=10)
