import unittest
import sys
import io
import os
from unittest.mock import MagicMock, patch

# Ensure src is in path so we can import html2md
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import html2md.cli

class TestCliProcessUrlError(unittest.TestCase):
    def test_process_url_generic_exception(self):
        """Test that a generic Exception in process_url is caught and printed."""

        # We need to mock requests and markdownify modules because they might not be installed
        mock_requests = MagicMock()

        # Create a mock RequestException that inherits from Exception so except clauses work
        # This is important for the `except requests.RequestException` block to not match `Exception` incorrectly
        # if the mock type hierarchy isn't set up.
        class MockRequestException(Exception): pass
        mock_requests.RequestException = MockRequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session

        # Configure the session.get to raise a generic Exception
        # This targets the `except Exception as e:` block in cli.py
        mock_session.get.side_effect = Exception('Unexpected failure')

        mock_markdownify = MagicMock()

        # Capture stderr to verify the error message
        captured_stderr = io.StringIO()

        # Patch the modules into sys.modules
        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            # Patch stderr to capture the print output
            with patch('sys.stderr', captured_stderr):
                # Run the main function with a URL argument
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except Exception as e:
                    self.fail(f'main raised exception {e}')

        output = captured_stderr.getvalue()
        # Verify that the specific error message from the except block is present
        self.assertIn('Conversion failed: Unexpected failure', output)

if __name__ == '__main__':
    unittest.main()
