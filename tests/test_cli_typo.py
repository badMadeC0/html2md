"""Tests for html2md CLI typo correction paths."""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import os

# Ensure src is in path before importing the local package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import html2md.cli  # pylint: disable=wrong-import-position


class TestCliUrlTypo(unittest.TestCase):
    """Unit tests for URL typo correction in CLI."""

    def test_url_typo_trailing_slash_query(self):
        """Test that trailing slash before query parameters is removed."""
        captured_stderr = io.StringIO()
        captured_stdout = io.StringIO()

        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session

        mock_resp = MagicMock()
        mock_resp.text = "<h1>Hello</h1>"
        mock_resp.status_code = 200
        mock_session.get.return_value = mock_resp

        mock_markdownify = MagicMock()
        mock_markdownify.markdownify.return_value = "# Hello"

        with patch.dict(
            sys.modules, {"requests": mock_requests, "markdownify": mock_markdownify}
        ):
            with patch("sys.stderr", captured_stderr), patch(
                "sys.stdout", captured_stdout
            ):
                try:
                    html2md.cli.main(["--url", "http://example.com/?foo=bar"])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

        # Assert that session.get was called with the corrected URL
        mock_session.get.assert_called_once_with(
            "http://example.com?foo=bar", timeout=30
        )
