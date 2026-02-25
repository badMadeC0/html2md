import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

# Define a mock exception class
class MockRequestException(Exception):
    pass

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.exceptions.RequestException is caught and logged as Network error."""

    # Create mocks
    mock_requests = MagicMock()
    # IMPORTANT: Make exceptions.RequestException a real class we can catch
    mock_requests.exceptions.RequestException = MockRequestException

    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = MockRequestException("Connection refused")

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
    # New message format
    assert "Network error: Connection refused" in caplog.text
    # Should NOT hit the generic catch
    assert "Conversion failed" not in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_file_error(capsys, caplog):
    """Test that OSError is caught and logged as File I/O error."""

    mock_requests = MagicMock()
    mock_requests.exceptions.RequestException = MockRequestException
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Success response
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Markdown success
    mock_markdownify.markdownify.return_value = "# Header"

    # Make os.makedirs fail
    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            with patch('os.makedirs', side_effect=OSError("Disk full")):
                # Run main with --outdir to trigger file ops
                exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', 'out'])

    assert exit_code == 0
    assert "File I/O error: Disk full" in caplog.text
    assert "Conversion failed" not in caplog.text


def test_cli_conversion_markdownify_failure(capsys, caplog):
    """Test that generic failure (e.g. markdownify parse error) is caught by generic handler."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.exceptions.RequestException = MockRequestException
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
    assert "Conversion failed: Parse error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out
