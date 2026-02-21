import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html2md.cli import main
import requests
class TestCliExceptions(unittest.TestCase):
    def setUp(self):
        # Suppress output during tests
        self.captured_output = io.StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.captured_output

    def tearDown(self):
        sys.stdout = self.original_stdout

    def test_network_error(self):
        """Test that network errors are caught and printed."""
        if 'requests' not in sys.modules:
            self.skipTest("requests module not available")

        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network unreachable")

            try:
                main(['--url', 'http://example.com'])
            except Exception as e:
                self.fail(f"main raised exception {e}")

            output = self.captured_output.getvalue()
            # Expect "Network error: Network unreachable"
            self.assertIn("Network error", output)
            self.assertIn("Network unreachable", output)

    def test_file_error(self):
        """Test that file I/O errors are caught and printed."""
        if 'requests' not in sys.modules:
            self.skipTest("requests module not available")

        with patch('requests.Session.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = "<h1>Hello</h1>"
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp

            with patch('markdownify.markdownify', return_value="# Hello"):
                with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                    with patch('builtins.open', side_effect=OSError("Permission denied")):
                         try:
                             main(['--url', 'http://example.com', '--outdir', 'dummy'])
                         except Exception as e:
                             self.fail(f"main raised exception {e}")

                         output = self.captured_output.getvalue()
                         # Expect "File error: Permission denied"
                         self.assertIn("File error", output)
                         self.assertIn("Permission denied", output)
