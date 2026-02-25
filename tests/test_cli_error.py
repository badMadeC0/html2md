import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

# Helper to mock RequestException since it must be an exception class
class MockRequestException(Exception):
    pass

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.get failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.RequestException = MockRequestException # Assign valid exception class
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = MockRequestException("Network error")

    # We must patch sys.modules so that the 'import requests' inside main() gets our mock
    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            # Run main
            exit_code = html2md.cli.main(['--url', 'http://example.com'])

    # Verify exit code
    assert exit_code == 0

    # Verify log messages (via logging, not stdout)
    assert "Processing URL: http://example.com" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Conversion failed: Network error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_os_error_failure(capsys, caplog):
    """Test that OSError (e.g. file write failure) is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.RequestException = MockRequestException
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to succeed
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Configure markdownify to succeed
    mock_markdownify.markdownify.return_value = "# Markdown Content"

    # We mock os.makedirs to raise OSError
    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            # We also need to patch os.makedirs in html2md.cli
            with patch('html2md.cli.os.makedirs', side_effect=OSError("Permission denied")):
                 # We must provide --outdir to trigger file operations
                exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', '/tmp/output'])

    assert exit_code == 0

    # Verify log messages
    assert "Processing URL: http://example.com" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Converting to Markdown" in caplog.text
    assert "Conversion failed: Permission denied" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out
