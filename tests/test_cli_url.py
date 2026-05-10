"""Tests for URL handling in CLI."""

import sys
from unittest.mock import MagicMock, patch

from html2md import cli

def test_process_url_fixes_query_param_typo():
    """Test that URL query parameter typo (trailing slash before ?) is corrected."""

    # Mock requests and markdownify since we might not have them installed
    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<h1>Test</h1>"
    mock_session.get.return_value = mock_response

    mock_markdownify = MagicMock()
    mock_markdownify.markdownify.return_value = "# Test"

    # Test with a URL containing the typo
    url_with_typo = "http://example.com/?q=1"
    expected_corrected_url = "http://example.com?q=1"

    with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
        exit_code = cli.main(['--url', url_with_typo])

        assert exit_code == 0
        # Verify get was called with the corrected URL
        mock_session.get.assert_called_once_with(expected_corrected_url, timeout=30)
