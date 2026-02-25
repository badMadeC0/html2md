"""Tests that CLI log/progress messages go to stderr, not stdout."""

import logging
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch
import pytest

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

try:
    import requests
except ImportError:
    requests = None

def test_logging_not_on_stdout_success(capsys, caplog):
    """On successful conversion, only Markdown content appears on stdout.

    Progress messages like 'Processing URL', 'Fetching content...',
    and 'Converting to Markdown...' must go to stderr (via logging),
    not stdout.
    """
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()
    mock_bs4 = MagicMock()
    mock_reportlab_platypus = MagicMock()
    mock_reportlab_styles = MagicMock()

    # Configure requests mock to succeed
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_response = MagicMock()
    mock_response.text = "<h1>Hello</h1>"
    mock_session.get.return_value = mock_response

    # Configure markdownify mock to return Markdown
    mock_markdownify.markdownify.return_value = "# Hello"

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

    captured = capsys.readouterr()

    # Stdout must contain ONLY the converted Markdown
    assert "# Hello" in captured.out
    assert "Processing URL" not in captured.out
    assert "Fetching content" not in captured.out
    assert "Converting to Markdown" not in captured.out

    # Log records must contain progress messages
    assert "Processing URL" in caplog.text
    assert "Fetching content" in caplog.text
    assert "Converting to Markdown" in caplog.text


def _run_subprocess(args):
    """Run html2md as a subprocess and return the CompletedProcess."""
    env = os.environ.copy()
    src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_dir}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_dir

    return subprocess.run(
        [sys.executable, "-m", "html2md"] + args,
        capture_output=True, text=True, check=False, env=env,
    )

@pytest.mark.skipif(requests is None, reason="requests not installed")
def test_logging_output_subprocess():
    """When the URL cannot be reached, stdout must be empty.

    All error/progress messages must appear only on stderr.
    """
    result = _run_subprocess(['--url', 'http://127.0.0.1:12345/'])

    # Stdout must be empty — no progress or error messages
    assert result.stdout == ""

    # Stderr must contain the progress/error messages
    assert "Processing URL" in result.stderr

    # We expect "Network error" for connection issues, or "Conversion failed" fallback
    assert ("Network error" in result.stderr or "Conversion failed" in result.stderr)
