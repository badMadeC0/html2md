"""Tests for CLI logging behavior."""

import logging
import subprocess
import sys
import unittest.mock
import os
import socket
from html2md.cli import main

def test_logging_output(capsys):
    """Test that logs go to stderr and content output goes to stdout (mocked)."""

    # Mock requests
    mock_requests = unittest.mock.MagicMock()
    mock_response = unittest.mock.MagicMock()
    mock_response.text = "<html>content</html>"
    mock_response.status_code = 200
    # Important: Explicitly set is_redirect to False to avoid urljoin error
    mock_response.is_redirect = False

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
        # Mock getaddrinfo to return a public IP so validation passes
        with unittest.mock.patch('socket.getaddrinfo') as mock_dns:
            # Return a valid public IP (Google's DNS)
            mock_dns.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, '', ('8.8.8.8', 80))]

            # Run main with URL argument
            try:
                exit_code = main(['--url', 'http://example.com'])
            except SystemExit as e:
                exit_code = e.code

    assert exit_code == 0

    captured = capsys.readouterr()

    # Assert logs are in stderr
    assert "Processing URL: http://example.com" in captured.err
    assert "Fetching content from: http://example.com" in captured.err
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

    if result.returncode == 1:
        # Dependency failure
        assert "Missing dependency" in result.stderr
    else:
        # Network failure
        assert result.returncode == 0
        # Logs in stderr
        assert "Processing URL" in result.stderr

        # New behavior: Validation failure prevents "Fetching content" log
        assert "URL validation failed" in result.stderr or "Could not resolve hostname" in result.stderr

    # Standard output should be empty
    assert result.stdout == ""
