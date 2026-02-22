import unittest
from unittest.mock import patch, MagicMock
import io
import os
import requests
from html2md.cli import main

class TestCliExceptions(unittest.TestCase):
    def test_network_error(self):
        """Test that network errors are caught and printed."""
        # Mock sys.stderr to capture output
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            # Patch requests.Session class instead of get method for better compatibility with mocks
            with patch('requests.Session') as mock_session_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session
                mock_session.get.side_effect = requests.RequestException("Network unreachable")

                try:
                    main(['--url', 'http://example.com'])
                except Exception as e:
                    self.fail(f"main raised exception {e}")

                output = captured_stderr.getvalue()
                # Expect "Network error: Network unreachable"
                self.assertIn("Network error", output)
                self.assertIn("Network unreachable", output)

    def test_file_error(self):
        """Test that file I/O errors are caught and printed."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session') as mock_session_cls:
                mock_session = MagicMock()
                mock_session_cls.return_value = mock_session

                mock_resp = MagicMock()
                # Updated for new implementation using iter_content and encoding
                mock_resp.iter_content.return_value = [b"<h1>Hello</h1>"]
                mock_resp.encoding = "utf-8"
                mock_resp.status_code = 200
                mock_session.get.return_value = mock_resp

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                        with patch('builtins.open', side_effect=OSError("Permission denied")):
                             try:
                                 main(['--url', 'http://example.com', '--outdir', 'dummy'])
                             except Exception as e:
                                 self.fail(f"main raised exception {e}")

                             output = captured_stderr.getvalue()
                             # Expect "File error: Permission denied"
                             self.assertIn("File error", output)
                             self.assertIn("Permission denied", output)
