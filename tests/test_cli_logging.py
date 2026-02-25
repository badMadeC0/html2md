"""Tests that CLI log/progress messages go to stderr, not stdout."""

import importlib
import logging
import os
import subprocess
import sys

import pytest

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli


def test_logging_not_on_stdout_success(capsys, caplog, cli_mocks):
    """On successful conversion, only Markdown content appears on stdout.

    Progress messages like 'Processing URL', 'Fetching content...',
    and 'Converting to Markdown...' must go to stderr (via logging),
    not stdout.
    """
    cli_mocks["response"].text = "<h1>Hello</h1>"
    cli_mocks["markdownify"].markdownify.return_value = "# Hello"

    with caplog.at_level(logging.INFO):
        exit_code = html2md.cli.main(["--url", "http://example.com"])

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
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


requests_missing = importlib.util.find_spec("requests") is None


@pytest.mark.skipif(requests_missing, reason="requests not installed")
def test_logging_output_subprocess():
    """When the URL cannot be reached, stdout must be empty.

    All error/progress messages must appear only on stderr.
    """
    result = _run_subprocess(["--url", "http://127.0.0.1:12345/"])

    # Stdout must be empty — no progress or error messages
    assert result.stdout == ""

    # Stderr must contain the progress/error messages
    assert "Processing URL" in result.stderr
    assert "Network error" in result.stderr
