"""Tests for upload functionality."""
import io
import sys
import unittest
from unittest.mock import MagicMock, patch

# Mock anthropic module if not installed
try:
    import anthropic
except ImportError:
    anthropic = MagicMock()
    # Define APIError as a real class so we can catch it
    class APIError(Exception):
        pass
    anthropic.APIError = APIError
    anthropic.Anthropic = MagicMock()
    sys.modules["anthropic"] = anthropic

from html2md import upload


class TestUploadFile(unittest.TestCase):
    """Tests for the upload_file function."""

    @patch("html2md.upload.anthropic.Anthropic")
    @patch("pathlib.Path.open")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.name", new_callable=unittest.mock.PropertyMock)
    @patch("mimetypes.guess_type")
    def test_upload_file_success(
        self, mock_guess_type, mock_path_name, mock_exists, mock_open, mock_anthropic
    ):
        """Test successful file upload."""
        # Setup mocks
        mock_exists.return_value = True
        mock_path_name.return_value = "test_file.txt"
        mock_guess_type.return_value = ("text/plain", None)

        mock_file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_result = MagicMock()
        mock_result.id = "file_12345"
        mock_client.beta.files.upload.return_value = mock_result

        # Call function
        result = upload.upload_file("test_file.txt")

        # Assertions
        mock_exists.assert_called_once()
        mock_guess_type.assert_called_once_with("test_file.txt")
        mock_open.assert_called_once_with(unittest.mock.ANY, "rb")
        mock_client.beta.files.upload.assert_called_once_with(
            file=("test_file.txt", mock_file_handle, "text/plain")
        )
        self.assertEqual(result, mock_result)

    @patch("pathlib.Path.exists")
    def test_upload_file_not_found(self, mock_exists):
        """Test file not found error."""
        mock_exists.return_value = False

        with self.assertRaises(FileNotFoundError):
            upload.upload_file("non_existent_file.txt")

    @patch("html2md.upload.anthropic.Anthropic")
    @patch("pathlib.Path.open")
    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.name", new_callable=unittest.mock.PropertyMock)
    @patch("mimetypes.guess_type")
    def test_upload_file_default_mime_type(
        self, mock_guess_type, mock_path_name, mock_exists, mock_open, mock_anthropic
    ):
        """Test default mime type when detection fails."""
        mock_exists.return_value = True
        mock_path_name.return_value = "unknown_file"
        mock_guess_type.return_value = (None, None)

        mock_file_handle = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file_handle

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        upload.upload_file("unknown_file")

        mock_client.beta.files.upload.assert_called_once()
        call_args = mock_client.beta.files.upload.call_args
        self.assertEqual(call_args.kwargs['file'][2], "application/octet-stream")


class TestUploadMain(unittest.TestCase):
    """Tests for the main function."""

    @patch("html2md.upload.upload_file")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_success(self, mock_stdout, mock_upload_file):
        """Test successful execution of main."""
        mock_result = MagicMock()
        mock_result.id = "file_123"
        mock_upload_file.return_value = mock_result

        ret = upload.main(["test_file.txt"])

        self.assertEqual(ret, 0)
        mock_upload_file.assert_called_once_with("test_file.txt")
        self.assertIn("File uploaded successfully. ID: file_123", mock_stdout.getvalue())

    @patch("html2md.upload.upload_file")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_file_not_found(self, mock_stderr, mock_upload_file):
        """Test main handling of FileNotFoundError."""
        mock_upload_file.side_effect = FileNotFoundError("File not found: bad_file.txt")

        ret = upload.main(["bad_file.txt"])

        self.assertEqual(ret, 1)
        self.assertIn("Error: File not found: bad_file.txt", mock_stderr.getvalue())

    @patch("html2md.upload.upload_file")
    @patch("sys.stderr", new_callable=io.StringIO)
    def test_main_api_error(self, mock_stderr, mock_upload_file):
        """Test main handling of Anthropic APIError."""
        # Use the mocked APIError class if anthropic is mocked
        # Otherwise use the real one, but here we can just rely on what upload_file raises
        # We need to ensure we raise the same exception class that main catches.

        # We need access to the APIError class used by the module under test
        from html2md.upload import anthropic as module_anthropic

        # Instantiate APIError
        # If it's the real one, it might need arguments. If it's our mock, it might not.
            error = module_anthropic.APIError("API Error occurred")

        mock_upload_file.side_effect = error

        ret = upload.main(["test_file.txt"])

        self.assertEqual(ret, 1)
        self.assertIn("API error: API Error occurred", mock_stderr.getvalue())
