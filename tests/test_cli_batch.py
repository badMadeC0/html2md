"""Tests for CLI --batch mode."""

import io
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path

# Ensure src is in path before importing the local package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from html2md.cli import main


class TestCliBatch(unittest.TestCase):
    """Unit tests for CLI --batch mode."""

    def test_batch_mode_success(self):
        """Test that batch mode successfully processes a file with URLs."""

        with tempfile.TemporaryDirectory() as tmp_dir:
            batch_file = Path(tmp_dir) / "urls.txt"
            # Write some URLs, including empty lines and spaces to test strip()
            urls_content = "http://example.com/1\n  \nhttp://example.com/2 \n\n"
            batch_file.write_text(urls_content, encoding="utf-8")

            captured_stdout = io.StringIO()
            captured_stderr = io.StringIO()

            with patch("sys.stdout", captured_stdout), patch(
                "sys.stderr", captured_stderr
            ):
                with patch("requests.Session.get") as mock_get:
                    mock_resp = MagicMock()
                    mock_resp.text = "<h1>Content</h1>"
                    mock_resp.status_code = 200
                    mock_get.return_value = mock_resp

                    with patch(
                        "markdownify.markdownify", return_value="# Content"
                    ) as mock_md:
                        # Call main with the batch file
                        result = main(["--batch", str(batch_file)])

                        # Verify the result and calls
                        self.assertEqual(result, 0)

                        # Verify exactly 2 calls were made to requests.get
                        self.assertEqual(mock_get.call_count, 2)

                        # Extract the URLs from the calls
                        # mock_get.call_args_list is a list of Call objects (args, kwargs)
                        called_urls = [call[0][0] for call in mock_get.call_args_list]
                        self.assertEqual(
                            called_urls,
                            ["http://example.com/1", "http://example.com/2"],
                        )

                        # Verify exactly 2 calls were made to markdownify
                        self.assertEqual(mock_md.call_count, 2)

                        output = captured_stdout.getvalue()
                        self.assertIn("Processing URL: http://example.com/1", output)
                        self.assertIn("Processing URL: http://example.com/2", output)

    def test_batch_mode_file_not_found(self):
        """Test that batch mode handles non-existent file correctly."""
        captured_stderr = io.StringIO()

        with tempfile.TemporaryDirectory() as tmp_dir:
            missing_file = str(Path(tmp_dir) / "nonexistent.txt")
            with patch("sys.stderr", captured_stderr):
                # Pass a file path that is guaranteed not to exist
                result = main(["--batch", missing_file])

                # The CLI logic returns 1 for missing batch file
                self.assertEqual(result, 1)

                error_output = captured_stderr.getvalue()
                self.assertIn(
                    f"Error: Batch file not found: {missing_file}",
                    error_output,
                )
