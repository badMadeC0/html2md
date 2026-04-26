import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os
import requests

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import html2md.cli

class TestCliError(unittest.TestCase):
    def test_cli_conversion_request_failure(self):
        """Test that requests.get failure is caught and printed."""

        # Configure requests mock to fail
        # Use a real RequestException so the except block catches it
        mock_requests = MagicMock()
        mock_requests.RequestException = requests.RequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_session.get.side_effect = requests.RequestException("Network error")

        mock_markdownify = MagicMock()

        # Capture stderr
        captured_stderr = io.StringIO()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('sys.stderr', captured_stderr):
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except Exception as e:
                    self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        self.assertIn("Network error", output)

    def test_cli_conversion_markdownify_failure(self):
        """Test that markdownify failure is caught and printed."""

        mock_requests = MagicMock()
        # We need RequestException to be valid for the except clause
        mock_requests.RequestException = requests.RequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_session.get.return_value = mock_response

        mock_markdownify = MagicMock()
        # Mocking the module attribute access
        mock_markdownify.markdownify.side_effect = Exception("Parse error")

        captured_stderr = io.StringIO()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('sys.stderr', captured_stderr):
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except Exception as e:
                    self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        # The code catches Exception and prints "Conversion failed: {e}"
        self.assertIn("Conversion failed", output)
        self.assertIn("Parse error", output)

if __name__ == '__main__':
    unittest.main()
