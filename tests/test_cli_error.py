import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os
import requests

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import html2md.cli

# Define a mock RequestException in case requests is not installed in the test env
class MockRequestException(Exception):
    pass

try:
    import requests
    RealRequestException = requests.RequestException
except ImportError:
    RealRequestException = MockRequestException

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.get failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.RequestException = RealRequestException  # Make it a catchable exception class

    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = RealRequestException("Network error")

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
    assert "Network error: Network error" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_file_error(capsys, caplog):
    """Test that OSError is caught and logged as File error."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.RequestException = RealRequestException

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

    mock_markdownify.markdownify.return_value = "# Header"

    # We patch os.makedirs to fail.
    # Since html2md.cli imports os at top level, we can patch 'html2md.cli.os.makedirs'
    # BUT, the code does 'if not os.path.exists(args.outdir): os.makedirs(args.outdir)'
    # So we need to ensure exists returns false, then makedirs raises OSError

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            # Patch os inside the module
            with patch('html2md.cli.os.makedirs', side_effect=OSError("Permission denied")):
                with patch('html2md.cli.os.path.exists', return_value=False):
                    exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', '/fail'])

    assert exit_code == 0
    assert "File error: Permission denied" in caplog.text


def test_cli_conversion_markdownify_failure(capsys, caplog):
    """Test that markdownify failure is caught and logged to stderr."""

    # Create mocks
    mock_requests = MagicMock()
    mock_requests.RequestException = RealRequestException

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
