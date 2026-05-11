"""Tests for html2md CLI error-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import os
import sys
import requests  # type: ignore[import-untyped]

# Ensure src is in path before importing the local package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import html2md.cli  # pylint: disable=wrong-import-position  # type: ignore[import-untyped]


class TestCliError(unittest.TestCase):
    """Unit tests for CLI network and conversion error handling."""

    def test_cli_conversion_request_failure(self):
        """Test that requests.get failure is caught and printed."""

        # Configure requests mock to fail
        # Use a real RequestException so the except block catches it
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.RequestException("Network error")

        # Capture stderr
        captured_stderr = io.StringIO()

        with patch('html2md.cli.requests.Session', return_value=mock_session):
            with patch('sys.stderr', captured_stderr):
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        self.assertIn("Network error", output)

    def test_cli_conversion_markdownify_failure(self):
        """Test that markdownify failure is caught and printed."""

        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_session.get.return_value = mock_response

        captured_stderr = io.StringIO()

        with patch('html2md.cli.requests.Session', return_value=mock_session):
            with patch('html2md.cli.md', side_effect=Exception("Parse error")):
                with patch('sys.stderr', captured_stderr):
                    try:
                        html2md.cli.main(['--url', 'http://example.com'])
                    except (SystemExit, RuntimeError, ValueError) as e:
                        self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        # The code catches Exception and prints "Conversion failed: {e}"
        self.assertIn("Conversion failed", output)
        self.assertIn("Parse error", output)

if __name__ == '__main__':
    unittest.main()
