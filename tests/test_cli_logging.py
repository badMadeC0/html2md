"""Tests for CLI logging behavior."""

import sys
import unittest.mock
import logging
from html2md.cli import main

def test_logging_output(capsys):
    """Test that logs go to stderr and content output goes to stdout."""

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
