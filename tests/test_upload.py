"""Tests for upload functionality."""

import sys
from unittest.mock import MagicMock, patch, mock_open

# Define a dummy APIError that inherits from Exception
class MockAPIError(Exception):
    pass

# Mock anthropic before importing html2md.upload
mock_anthropic = MagicMock()
mock_anthropic.APIError = MockAPIError
sys.modules["anthropic"] = mock_anthropic

from html2md.upload import upload_file, main  # type: ignore


def test_upload_file_success():
    """Test successful file upload."""
    file_path = "test_file.txt"
    file_content = b"content"
    mime_type = "text/plain"

    # Setup mocks
    mock_client_instance = mock_anthropic.Anthropic.return_value
    mock_upload = mock_client_instance.beta.files.upload
    mock_upload.return_value.id = "file_id_123"

    with patch("pathlib.Path.exists", return_value=True),          patch("pathlib.Path.open", mock_open(read_data=file_content)),          patch("mimetypes.guess_type", return_value=(mime_type, None)):

        result = upload_file(file_path)

        assert result.id == "file_id_123"
        mock_upload.assert_called_once()
        call_args = mock_upload.call_args
        assert call_args.kwargs["file"][0] == "test_file.txt"
        assert call_args.kwargs["file"][1].read() == file_content
        assert call_args.kwargs["file"][2] == mime_type


def test_upload_file_not_found():
    """Test file not found error."""
    with patch("pathlib.Path.exists", return_value=False):
        try:
            upload_file("nonexistent.txt")
        except FileNotFoundError:
            pass
        else:
            assert False, "FileNotFoundError not raised"


def test_upload_file_default_mime_type():
    """Test default mime type fallback."""
    file_path = "test_file.bin"
    file_content = b"binary_data"

    # Setup mocks
    mock_client_instance = mock_anthropic.Anthropic.return_value
    mock_upload = mock_client_instance.beta.files.upload
    mock_upload.return_value.id = "file_id_456"

    with patch("pathlib.Path.exists", return_value=True),          patch("pathlib.Path.open", mock_open(read_data=file_content)),          patch("mimetypes.guess_type", return_value=(None, None)):

        result = upload_file(file_path)

        assert result.id == "file_id_456"
        mock_upload.assert_called()
        call_args = mock_upload.call_args
        assert call_args.kwargs["file"][2] == "application/octet-stream"


def test_main_success(capsys):
    """Test CLI main function success."""
    argv = ["test_file.txt"]

    with patch("html2md.upload.upload_file") as mock_upload_file:
        mock_upload_file.return_value.id = "test_id"

        ret = main(argv)

        assert ret == 0
        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: test_id" in captured.out


def test_main_file_not_found(capsys):
    """Test CLI main function file not found error."""
    argv = ["nonexistent.txt"]

    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("File not found")):
        ret = main(argv)

        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err


def test_main_api_error(capsys):
    """Test CLI main function API error."""
    argv = ["test_file.txt"]

    # Mock APIError
    api_error = mock_anthropic.APIError("API Error")

    with patch("html2md.upload.upload_file", side_effect=api_error):
        ret = main(argv)

        assert ret == 1
        captured = capsys.readouterr()
        assert "API error: API Error" in captured.err
