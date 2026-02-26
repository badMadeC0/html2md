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

    mock_session = cli_mocks["session"]
    mock_session.get.side_effect = cli_mocks["requests_exceptions"].RequestException("Network failure")

    with caplog.at_level(logging.INFO):
        exit_code = html2md.cli.main(['--url', 'http://example.com'])

    assert exit_code == 0

    assert "Processing URL: http://example.com" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Network error: Network failure" in caplog.text

    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out


def test_cli_conversion_file_error(capsys, caplog, cli_mocks):
    """Test that OSError (e.g. file permission) is caught and logged."""

    with caplog.at_level(logging.INFO):
        with patch("builtins.open", side_effect=OSError("Permission denied")):
            with patch("os.path.exists", return_value=False), \
                    patch("os.makedirs"):
                exit_code = html2md.cli.main(['--url', 'http://example.com', '--outdir', 'output'])

    assert exit_code == 0
    assert "File error: Permission denied" in caplog.text


def test_cli_conversion_markdownify_failure(capsys, caplog, cli_mocks):
    """Test that markdownify failure is caught and logged to stderr."""

    cli_mocks["markdownify"].markdownify.side_effect = Exception("Parse error")

    with caplog.at_level(logging.INFO):
        exit_code = html2md.cli.main(['--url', 'http://example.com'])

    assert exit_code == 0

    assert "Processing URL: http://example.com" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Converting to Markdown" in caplog.text
    assert "Conversion failed: Parse error" in caplog.text

    captured = capsys.readouterr()
    assert "Processing URL" not in captured.out
    assert "Conversion failed" not in captured.out
