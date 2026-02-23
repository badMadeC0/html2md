"""Security tests for CLI URL validation."""

import sys
import unittest
import os
import tempfile
from unittest.mock import MagicMock, patch

# Mock dependencies before importing the module under test
sys.modules['requests'] = MagicMock()
sys.modules['markdownify'] = MagicMock()

from html2md.cli import process_url, main

class TestCliSecurity(unittest.TestCase):
    def setUp(self):
        self.session = MagicMock()
        self.session.headers = {}

        # Reset the mock for markdownify before each test
        sys.modules['markdownify'].markdownify = MagicMock(return_value="# Mock Markdown")

    def test_valid_https_url(self):
        """Test that a valid HTTPS URL is processed."""
        url = "https://example.com"
        process_url(url, self.session)
        self.session.get.assert_called_once_with(url, timeout=30)

    def test_valid_http_url(self):
        """Test that a valid HTTP URL is processed."""
        url = "http://example.com"
        process_url(url, self.session)
        self.session.get.assert_called_once_with(url, timeout=30)

    def test_invalid_scheme_file(self):
        """Test that file:// scheme is rejected."""
        url = "file:///etc/passwd"
        with patch('builtins.print') as mock_print:
            process_url(url, self.session)

            # verify session.get was NOT called
            self.session.get.assert_not_called()

            # verify warning was printed
            found_warning = False
            for call in mock_print.call_args_list:
                args, _ = call
                if "Warning: Invalid URL scheme" in args[0] and "'file'" in args[0]:
                    found_warning = True
                    break
            self.assertTrue(found_warning, "Warning message not printed for file scheme")

    def test_invalid_scheme_ftp(self):
        """Test that ftp:// scheme is rejected."""
        url = "ftp://example.com"
        with patch('builtins.print') as mock_print:
            process_url(url, self.session)
            self.session.get.assert_not_called()

            found_warning = False
            for call in mock_print.call_args_list:
                args, _ = call
                if "Warning: Invalid URL scheme" in args[0] and "'ftp'" in args[0]:
                    found_warning = True
                    break
            self.assertTrue(found_warning, "Warning message not printed for ftp scheme")

    def test_no_scheme(self):
        """Test that URL without scheme is rejected."""
        url = "example.com"
        with patch('builtins.print') as mock_print:
            process_url(url, self.session)
            self.session.get.assert_not_called()

            found_warning = False
            for call in mock_print.call_args_list:
                args, _ = call
                if "Warning: Invalid URL scheme" in args[0]:
                    found_warning = True
                    break
            self.assertTrue(found_warning, "Warning message not printed for missing scheme")

    def test_batch_flow(self):
        """Test batch flow invokes process_url for each line."""
        # Create a real temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("https://good.com\nfile:///bad\nhttp://also-good.com")
            batch_path = f.name

        try:
            # We assume main calls process_url, so we mock process_url to check calls
            with patch('html2md.cli.process_url') as mock_process_url,                  patch('requests.Session', return_value=self.session):

                main(['--batch', batch_path])

                self.assertEqual(mock_process_url.call_count, 3)
                mock_process_url.assert_any_call("https://good.com", self.session, None)
                mock_process_url.assert_any_call("file:///bad", self.session, None)
                mock_process_url.assert_any_call("http://also-good.com", self.session, None)
        finally:
            os.remove(batch_path)

if __name__ == '__main__':
    unittest.main()
