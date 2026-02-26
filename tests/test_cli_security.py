import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import logging

# Ensure src path is correct
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from html2md.cli import main

class TestSecurityFix(unittest.TestCase):
    def setUp(self):
        # Create mocks
        self.mock_requests = MagicMock()
        self.mock_md = MagicMock()
        self.mock_session = MagicMock()
        self.mock_response = MagicMock()

        # Setup mocks
        self.mock_session.get.return_value = self.mock_response
        self.mock_response.text = "<html>Content</html>"
        self.mock_response.raise_for_status = MagicMock()
        self.mock_requests.Session.return_value = self.mock_session
        self.mock_md.markdownify = MagicMock(return_value="# Content")

        # Patch sys.modules to inject mocks
        # We need to patch before main is imported or re-imported if possible
        # Since main imports inside the function, patching sys.modules works.
        self.patcher = patch.dict(sys.modules, {
            'requests': self.mock_requests,
            'markdownify': self.mock_md
        })
        self.patcher.start()

        # Configure logging to capture output
        logging.getLogger().setLevel(logging.INFO)

    def tearDown(self):
        self.patcher.stop()

    def test_https_url_allowed(self):
        """Verify HTTPS URLs are processed correctly."""
        with patch('builtins.print'):
            main(['--url', 'https://example.com'])
        self.mock_session.get.assert_called()
        args, _ = self.mock_session.get.call_args
        self.assertEqual(args[0], 'https://example.com')

    def test_http_url_blocked(self):
        """Verify HTTP URLs are rejected and logged as error."""
        with patch('builtins.print'):
             with self.assertLogs(level='ERROR') as cm:
                 main(['--url', 'http://example.com'])

             # Check for specific error message
             self.assertTrue(any("Invalid URL scheme" in o for o in cm.output),
                             f"Expected 'Invalid URL scheme' in logs, got: {cm.output}")

             # Verify network request was NOT made
             self.mock_session.get.assert_not_called()

    def test_ftp_url_blocked(self):
        """Verify FTP URLs are rejected."""
        with self.assertLogs(level='ERROR') as cm:
            main(['--url', 'ftp://example.com'])
        self.assertTrue(any("Invalid URL scheme" in o for o in cm.output))
        self.mock_session.get.assert_not_called()
             with self.assertLogs(level='ERROR') as cm:
                 main(['--url', 'ftp://example.com'])
             self.assertTrue(any("Invalid URL scheme" in o for o in cm.output))
             self.mock_session.get.assert_not_called()

    def test_file_url_blocked(self):
        """Verify FILE URLs are rejected."""
        with patch('builtins.print'):
             with self.assertLogs(level='ERROR') as cm:
                 main(['--url', 'file:///etc/passwd'])
             self.assertTrue(any("Invalid URL scheme" in o for o in cm.output))
             self.mock_session.get.assert_not_called()
