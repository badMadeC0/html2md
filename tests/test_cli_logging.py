"""Tests for CLI logging behavior."""

import logging
import subprocess
import sys
import unittest.mock
import os
from html2md.cli import main

def test_logging_output(capsys):
    """Test that logs go to stderr and content output goes to stdout (mocked)."""

    # Mock requests
    mock_requests = unittest.mock.MagicMock()
    mock_response = unittest.mock.MagicMock()
    mock_response.text = "<html>content</html>"
    mock_response.status_code = 200
    mock_requests.Session.return_value.get.return_value = mock_response

    # Mock markdownify module
    mock_md_module = unittest.mock.MagicMock()
    mock_md_module.markdownify.return_value = "# Markdown Content"

    # Reset logging handlers to ensure basicConfig in main() takes effect
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Patch sys.modules to mock imports inside main()
    with unittest.mock.patch.dict(sys.modules, {
        'requests': mock_requests,
        'markdownify': mock_md_module
    }):
        # Run main with URL argument
        try:
            exit_code = main(['--url', 'http://example.com'])
        except SystemExit as e:
            exit_code = e.code

    assert exit_code == 0

    captured = capsys.readouterr()

    # Assert logs are in stderr
    assert "Processing URL: http://example.com" in captured.err
    assert "Fetching content..." in captured.err
    assert "Converting to Markdown..." in captured.err

    # Assert content is in stdout
    assert "# Markdown Content" in captured.out

    # Assert logs are NOT in stdout
    assert "Processing URL" not in captured.out

def test_logging_output_subprocess():
    """Test that logs go to stderr and output goes to stdout (via subprocess failure case)."""
    # This test ensures logging configuration works in a real subprocess environment.

    cmd = [sys.executable, "-m", "html2md", "--url", "http://nonexistent.test"]

    # Ensure src is in PYTHONPATH
    env = os.environ.copy()
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env
    )

    # In both missing dependency case (return code 1) and network failure case (return code 0 with error log),
    # the logs should go to stderr.

    if result.returncode == 1:
        # Dependency failure
        # Check stderr for dependency error
        assert "Missing dependency" in result.stderr
    else:
        # Network failure
        assert result.returncode == 0
        # Logs in stderr
        assert "Processing URL" in result.stderr
        assert "Fetching content..." in result.stderr
        assert "Conversion failed" in result.stderr

    # Standard output should be empty (no markdown)
    assert result.stdout == ""
