import argparse
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import anthropic

from html2md.upload import main, upload_file


class TestUploadFile(unittest.TestCase):
    def test_upload_missing_file(self):
        """Test that upload_file raises FileNotFoundError for missing file."""
        with patch.object(Path, "exists", return_value=False):
            with self.assertRaises(FileNotFoundError) as cm:
                upload_file("missing.txt")
            self.assertIn("File not found: missing.txt", str(cm.exception))

    @patch("anthropic.Anthropic")
    @patch("mimetypes.guess_type")
    def test_upload_success_known_mimetype(self, mock_guess_type, mock_anthropic):
        """Test successful upload with a known mimetype."""
        mock_guess_type.return_value = ("text/plain", None)

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_result = MagicMock()
        mock_client.beta.files.upload.return_value = mock_result

        m_open = mock_open(read_data=b"test data")

        with patch.object(Path, "exists", return_value=True):
            with patch("pathlib.Path.open", m_open):
                result = upload_file("test.txt")

        self.assertEqual(result, mock_result)
        mock_client.beta.files.upload.assert_called_once()
        _, kwargs = mock_client.beta.files.upload.call_args
        self.assertEqual(kwargs["file"][0], "test.txt")
        self.assertEqual(kwargs["file"][2], "text/plain")

    @patch("anthropic.Anthropic")
    @patch("mimetypes.guess_type")
    def test_upload_success_unknown_mimetype(self, mock_guess_type, mock_anthropic):
        """Test successful upload falls back to application/octet-stream."""
        mock_guess_type.return_value = (None, None)

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        mock_result = MagicMock()
        mock_client.beta.files.upload.return_value = mock_result

        m_open = mock_open(read_data=b"data")

        with patch.object(Path, "exists", return_value=True):
            with patch("pathlib.Path.open", m_open):
                result = upload_file("unknown.ext")

        self.assertEqual(result, mock_result)
        mock_client.beta.files.upload.assert_called_once()
        _, kwargs = mock_client.beta.files.upload.call_args
        self.assertEqual(kwargs["file"][0], "unknown.ext")
        self.assertEqual(kwargs["file"][2], "application/octet-stream")


class TestUploadMain(unittest.TestCase):
    @patch("html2md.upload.upload_file")
    def test_main_success(self, mock_upload_file):
        """Test main returns 0 on successful upload."""
        mock_result = MagicMock()
        mock_result.id = "file_123"
        mock_upload_file.return_value = mock_result

        captured_stdout = io.StringIO()
        with patch("sys.stdout", captured_stdout):
            exit_code = main(["test.txt"])

        self.assertEqual(exit_code, 0)
        self.assertIn(
            "File uploaded successfully. ID: file_123", captured_stdout.getvalue()
        )
        mock_upload_file.assert_called_once_with("test.txt")

    @patch("html2md.upload.upload_file")
    def test_main_file_not_found(self, mock_upload_file):
        """Test main returns 1 on FileNotFoundError."""
        mock_upload_file.side_effect = FileNotFoundError("File not found: test.txt")

        captured_stderr = io.StringIO()
        with patch("sys.stderr", captured_stderr):
            exit_code = main(["test.txt"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: File not found: test.txt", captured_stderr.getvalue())

    @patch("html2md.upload.upload_file")
    def test_main_api_error(self, mock_upload_file):
        """Test main returns 1 on anthropic.APIError."""
        mock_error = anthropic.APIStatusError(
            "API rate limit exceeded", response=MagicMock(), body=None
        )
        mock_upload_file.side_effect = mock_error

        captured_stderr = io.StringIO()
        with patch("sys.stderr", captured_stderr):
            exit_code = main(["test.txt"])

        self.assertEqual(exit_code, 1)
        self.assertIn("API error: API rate limit exceeded", captured_stderr.getvalue())

    def test_main_execution(self):
        """Test the execution block."""
        import runpy
        import html2md.upload
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(delete=False) as tf:
            tf.write(b"test data")
            temp_name = tf.name

        try:
            with patch("sys.argv", ["html2md-upload", temp_name]):
                with patch("anthropic.Anthropic") as mock_anthropic:
                    mock_result = MagicMock()
                    mock_result.id = "file_123"
                    mock_anthropic.return_value.beta.files.upload.return_value = (
                        mock_result
                    )

                    with self.assertRaises(SystemExit) as cm:
                        runpy.run_path(html2md.upload.__file__, run_name="__main__")

            self.assertEqual(cm.exception.code, 0)
        finally:
            os.remove(temp_name)
