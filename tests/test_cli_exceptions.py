"""Tests for CLI exception handling and verbose mode."""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from html2md.cli import main


class TestCliExceptions(unittest.TestCase):
    """Test CLI exception handling."""

    @patch("requests.Session")
    def test_unexpected_exception_no_verbose(self, mock_session_cls):
        """Test that unexpected exceptions are caught and printed without --verbose."""
        # Setup mock to raise a generic Exception
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = Exception("Unexpected Error")

        # Capture stderr
        from io import StringIO

        captured_stderr = StringIO()
        original_stderr = sys.stderr
        sys.stderr = captured_stderr

        try:
            # Run CLI
            exit_code = main(["--url", "http://example.com"])

            # Verify exit code is 0 (handled error)
            # The current implementation catches generic Exception and prints it,
            # but doesn't return non-zero exit code in the catch block (it falls through).
            # Wait, let's check cli.py again.
            # It prints "Conversion failed" and continues.
            # If args.url is processed, it returns 0 at the end.
            self.assertEqual(exit_code, 0)

            # Verify error message
            output = captured_stderr.getvalue()
            self.assertIn("Conversion failed: Unexpected Error", output)

        finally:
            sys.stderr = original_stderr

    @patch("requests.Session")
    def test_unexpected_exception_with_verbose(self, mock_session_cls):
        """Test that unexpected exceptions are raised with --verbose."""
        # Setup mock to raise a generic Exception
        mock_session = mock_session_cls.return_value
        mock_session.get.side_effect = Exception("Unexpected Error")

        # Verify exception is raised
        with self.assertRaises(Exception) as cm:
            main(["--url", "http://example.com", "--verbose"])

        self.assertEqual(str(cm.exception), "Unexpected Error")


if __name__ == "__main__":
    unittest.main()
