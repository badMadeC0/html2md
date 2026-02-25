import sys
import unittest
from unittest.mock import MagicMock, patch
import io
import logging

# Mock missing modules
sys.modules["requests"] = MagicMock()
sys.modules["markdownify"] = MagicMock()
sys.modules["bs4"] = MagicMock()
sys.modules["reportlab"] = MagicMock()
sys.modules["reportlab.platypus"] = MagicMock()
sys.modules["reportlab.lib.styles"] = MagicMock()

# Now import the module under test
from html2md import cli

class TestCredentialLeak(unittest.TestCase):
    def test_credential_leak_in_logs(self):
        # Prepare to capture stderr
        captured_stderr = io.StringIO()

        # Mock requests.Session().get()
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "<html><body>Content</body></html>"
        mock_session.get.return_value = mock_response

        # Reset logging handlers to allow basicConfig to work properly
        logger = logging.getLogger()
        for h in logger.handlers[:]:
            logger.removeHandler(h)

        with patch("sys.stderr", captured_stderr):
            with patch("requests.Session", return_value=mock_session):
                # Run the CLI processing
                # We use a mocked URL with credentials
                url = "http://user:password@example.com"
                cli.main(["--url", url])

        # Check logs
        log_contents = captured_stderr.getvalue()
        # print("\nCaptured Logs:\n", log_contents)

        # Verify fix
        self.assertNotIn("user:password@", log_contents, "FAIL: Credentials leaked in logs!")
        self.assertIn("user:***@", log_contents, "FAIL: Redacted URL not found in logs!")
        print("SUCCESS: Credentials successfully redacted in logs.")

if __name__ == "__main__":
    unittest.main()
