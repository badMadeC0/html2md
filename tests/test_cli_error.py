import logging
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

def setup_mock_requests():
    """Helper to create a mock requests module with a valid RequestException."""
    mock_requests = MagicMock()
    class MockRequestException(Exception):
        pass
    mock_requests.RequestException = MockRequestException
    return mock_requests, MockRequestException

def test_cli_conversion_request_failure(capsys, caplog):
    """Test that requests.get failure is caught and logged to stderr."""

    mock_requests, MockRequestException = setup_mock_requests()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
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
    assert "Network error: Connection refused" in caplog.text

    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_markdownify_failure(capsys, caplog):
    """Test that markdownify failure is caught and logged to stderr."""

    mock_requests, _ = setup_mock_requests()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

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
    assert "Conversion failed: Parse error" in caplog.text


def test_cli_conversion_file_error(capsys, caplog):
    """Test that file I/O errors are caught and logged."""

    mock_requests, _ = setup_mock_requests()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_session.get.return_value = mock_response

    mock_markdownify.markdownify.return_value = "# Markdown Content"

    with caplog.at_level(logging.INFO):
        with patch.dict(sys.modules, {
            'requests': mock_requests,
            'markdownify': mock_markdownify,
            'bs4': mock_bs4,
            'reportlab.platypus': mock_reportlab_platypus,
            'reportlab.lib.styles': mock_reportlab_styles,
        }):
            with patch('builtins.open', side_effect=OSError("Disk full")):
                with patch('os.makedirs'):
                     with patch('os.path.exists', return_value=False):
                        exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', 'output'])

    assert exit_code == 0
    assert "File error: Disk full" in caplog.text
