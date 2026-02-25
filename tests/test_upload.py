import unittest
import tempfile
import os
from unittest.mock import MagicMock, patch
import sys

# Ensure src is in path
sys.path.append("src")

# Mock anthropic BEFORE importing html2md.upload
sys.modules["anthropic"] = MagicMock()

import html2md.upload

class TestUpload(unittest.TestCase):
    def setUp(self):
        # Create a temporary file
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"dummy content")
        self.temp_file.close()

    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_client_is_reused(self):
        """Verify that the Anthropic client is instantiated only once across multiple calls."""

        # We need to access the mocked module
        import anthropic

        # Reset the global variable if it exists (simulate clean state)
        if hasattr(html2md.upload, "_CLIENT"):
            html2md.upload._CLIENT = None

        # Call the function twice
        try:
            html2md.upload.upload_file(self.temp_file.name)
            html2md.upload.upload_file(self.temp_file.name)
        except Exception as e:
            self.fail(f"upload_file raised exception: {e}")

        # Assertions
        # This should pass (called once)
        self.assertEqual(anthropic.Anthropic.call_count, 1, f"Expected 1 call, got {anthropic.Anthropic.call_count}")

if __name__ == "__main__":
    unittest.main()
