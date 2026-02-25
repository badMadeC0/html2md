import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.get failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = Exception("Network error")

    # Mock RequestException for the import
    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException

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

    # Verify that generic exceptions are caught and logged as unexpected errors
    assert "Unexpected error processing http://example.com: Network error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_markdownify_failure(capsys, caplog):
    """Test that markdownify failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
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

    # Mock RequestException for the import
    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException

    # Configure markdownify mock to fail
    # Note: in main(), it does 'from markdownify import markdownify as md'
    mock_markdownify.markdownify.side_effect = Exception("Parse error")

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            exit_code = html2md.cli.main(['--url', 'http://example.com'])

    assert exit_code == 0

    # Verify log messages (via logging, not stdout)
    assert "Processing URL: http://example.com" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Converting to Markdown" in caplog.text
    # Should be caught by generic exception handler
    assert "Unexpected error processing http://example.com: Parse error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out

def test_cli_conversion_request_exception(capsys, caplog):
    """Test that requests.RequestException is caught and logged as a network error."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail with RequestException
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException

    mock_session.get.side_effect = MockRequestException("Connection refused")

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            exit_code = html2md.cli.main(['--url', 'http://example.com'])

    assert exit_code == 0
    assert "Network error processing http://example.com: Connection refused" in caplog.text

def test_cli_conversion_os_error(capsys, caplog):
    """Test that OSError is caught and logged as a file I/O error."""

    # Create mocks
    mock_requests = MagicMock()
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

    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException

    # Mock markdownify to return content
    mock_markdownify.markdownify.return_value = "# Markdown Content"

    # We want to trigger OSError during file writing.
    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
             with patch("builtins.open", side_effect=OSError("Disk full")):
                # We need outdir to trigger file write
                exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', '/tmp/out'])

    assert exit_code == 0
    assert "File I/O error: Disk full" in caplog.text
