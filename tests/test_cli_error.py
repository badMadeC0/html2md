import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

# Define a specific exception for mocking RequestException
class MockRequestException(Exception):
    pass

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.get failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail with a RequestException
    mock_requests.RequestException = MockRequestException

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
    # Updated expectation: specific error message
    assert "Network error: Connection refused" in caplog.text

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

    # ESSENTIAL: RequestException must be a specific Exception class, not base Exception
    mock_requests.RequestException = MockRequestException

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
    # Still catches generic exceptions
    assert "Conversion failed: Parse error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out

def test_cli_conversion_file_error(capsys, caplog):
    """Test that file I/O errors are caught and logged."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # ESSENTIAL: RequestException must be a specific Exception class
    mock_requests.RequestException = MockRequestException

    # Configure requests mock to succeed
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Configure markdownify to succeed
    mock_markdownify.markdownify.return_value = "# Markdown Content"

    # We patch open to raise OSError
    # We also need to patch os.path.exists to return False so it tries to create dir or verify path
    # But get_unique_filepath uses os.path.exists.

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            # Patch open to fail when writing
            with patch('builtins.open', side_effect=OSError("Disk full")):
                # Also patch os.makedirs to succeed if called
                with patch('os.makedirs'):
                     # Also patch os.path.exists so get_unique_filepath works (returns false => file doesn't exist)
                     with patch('os.path.exists', return_value=False):
                        exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', 'output'])

    assert exit_code == 0
    assert "File error: Disk full" in caplog.text
