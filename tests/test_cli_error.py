import logging
import sys
import os
from unittest.mock import patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli


def test_cli_conversion_request_failure(capsys, caplog, cli_mocks):
    """Test that requests.get failure is caught and logged to stderr."""

    # Configure requests mock to fail
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_requests.exceptions.RequestException = type('RequestException', (Exception,), {})
    mock_session.get.side_effect = mock_requests.exceptions.RequestException("Network failure")

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'requests.exceptions': mock_requests.exceptions,
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
    assert "Network error: Network failure" in caplog.text

    # Verify nothing leaked to stdout
    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_file_error(capsys, caplog):
    """Test that OSError (e.g. file permission) is caught and logged."""

    # Create mocks
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests to succeed
    mock_session = MagicMock()
    mock_requests.exceptions.RequestException = type('RequestException', (Exception,), {})
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    # Configure markdownify to succeed
    mock_markdownify.markdownify.return_value = "Markdown Content"

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'requests.exceptions': mock_requests.exceptions,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
             with patch("builtins.open", side_effect=OSError("Permission denied")):
                 with patch("os.path.exists", return_value=False),                       patch("os.makedirs"):
                    exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', 'output'])

    assert exit_code == 0
    assert "File error: Permission denied" in caplog.text


def test_cli_conversion_markdownify_failure(capsys, caplog):
    """Test that markdownify failure is caught and logged to stderr."""


    # Configure requests mock to succeed
    mock_session = MagicMock()
    mock_requests.exceptions.RequestException = type('RequestException', (Exception,), {})
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    cli_mocks["markdownify"].markdownify.side_effect = Exception("Parse error")

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'requests.exceptions': mock_requests.exceptions,
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
