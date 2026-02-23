import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

def test_cli_conversion_request_failure(capsys):
    """Test that requests.get failure is caught and printed."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = Exception("Network error")

    # We must patch sys.modules so that the 'import requests' inside main() gets our mock
    # We also mock markdownify since it's imported in the same block
    with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
        # Run main
        exit_code = html2md.cli.main(['--url', 'http://example.com'])

    # Verify exit code
    assert exit_code == 0

    # Verify output
    captured = capsys.readouterr()
    assert "Processing URL: http://example.com" in captured.out
    assert "Fetching content..." in captured.out
    assert "Conversion failed: Network error" in captured.out


def test_cli_conversion_markdownify_failure(capsys):
    """Test that markdownify failure is caught and printed."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()

    # Configure requests mock to succeed
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Configure markdownify mock to fail
    # Note: in main(), it does 'from markdownify import markdownify as md'
    # When we mock the module 'markdownify', importing 'markdownify' from it returns the attribute.
    # So we need to ensure the attribute raises exception when called.
    mock_markdownify.markdownify.side_effect = Exception("Parse error")

    with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
        exit_code = html2md.cli.main(['--url', 'http://example.com'])

    assert exit_code == 0

    captured = capsys.readouterr()
    assert "Processing URL: http://example.com" in captured.out
    assert "Fetching content..." in captured.out
    assert "Converting to Markdown..." in captured.out
    assert "Conversion failed: Parse error" in captured.out
