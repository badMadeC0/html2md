import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# We need to handle the case where requests is not installed in the environment running the test
# But we assume it is.
try:
    from html2md.cli import main
    import requests
except ImportError:
    main = None
    requests = None

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
        # Check if requests is available
        if 'requests' not in sys.modules:
            self.skipTest("requests module not available")

        # Mock requests.Session.get to raise RequestException
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Network unreachable")

            try:
                main(['--url', 'http://example.com'])
            except Exception as e:
                self.fail(f"main raised exception {e}")

            output = self.captured_output.getvalue()
            # New behavior: "Network error: Network unreachable"
            self.assertIn("Network error", output)
            self.assertIn("Network unreachable", output)

    def test_file_error(self):
        """Test that file I/O errors are caught and printed."""
        if 'requests' not in sys.modules:
            self.skipTest("requests module not available")

        # Mock successful network request
        with patch('requests.Session.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = "<h1>Hello</h1>"
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp

            # Mock markdownify
            with patch('markdownify.markdownify', return_value="# Hello"):
                # Mock os.makedirs and os.path.exists
                with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                    # Mock open to raise OSError
                    # We must patch 'builtins.open'
                    with patch('builtins.open', side_effect=OSError("Permission denied")):
                         try:
                             # We need --outdir to trigger file writing
                             main(['--url', 'http://example.com', '--outdir', 'dummy'])
                         except Exception as e:
                             self.fail(f"main raised exception {e}")

                         output = self.captured_output.getvalue()
                         # New behavior: "File error: Permission denied"
                         self.assertIn("File error", output)
                         self.assertIn("Permission denied", output)
