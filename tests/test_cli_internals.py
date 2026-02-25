"""Tests for CLI internals."""

import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Use string import to avoid actual import if deps missing
# But we need main to be imported. It doesn't import deps at top level so safe.
from html2md.cli import main
from html2md.constants import DEFAULT_REQUEST_HEADERS

class TestCLIInternals(unittest.TestCase):
    """Test CLI internals."""

    def test_default_headers_are_used(self):
        """Test that default headers are applied to the session."""

        # Create mock modules
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session

        mock_md_module = MagicMock()
        mock_md_module.markdownify.return_value = "mocked markdown"

        # Inject mocks into sys.modules so imports succeed
        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_md_module}):
            # Setup response for get
            mock_response = MagicMock()
            mock_response.text = "<html></html>"
            mock_session.get.return_value = mock_response

            # Run main
            # We pass a mocked url
            exit_code = main(['--url', 'http://example.com'])

            # Verify exit code
            self.assertEqual(exit_code, 0)

            # Verify update called with DEFAULT_REQUEST_HEADERS
            mock_session.headers.update.assert_called_with(DEFAULT_REQUEST_HEADERS)

if __name__ == '__main__':
    unittest.main()
