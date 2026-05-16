import sys
from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import anthropic
import pytest

from html2md.upload import main, upload_file


def test_upload_file_not_found():
    """Test that uploading a non-existent file raises FileNotFoundError."""
    with patch("html2md.upload.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError, match="File not found: nonexistent.txt"):
            upload_file("nonexistent.txt")


def test_upload_file_success():
    """Test successful file upload."""
    mock_client = MagicMock()
    mock_upload_result = MagicMock()
    mock_client.beta.files.upload.return_value = mock_upload_result

    with patch("html2md.upload.Path.exists", return_value=True), patch(
        "html2md.upload.mimetypes.guess_type", return_value=("text/plain", None)
    ), patch("html2md.upload.anthropic.Anthropic", return_value=mock_client), patch(
        "html2md.upload.Path.open", mock_open(read_data=b"test data")
    ), patch(
        "html2md.upload.Path.name", "test.txt", create=True
    ):

        result = upload_file("test.txt")

        assert result == mock_upload_result
        mock_client.beta.files.upload.assert_called_once()
        call_args = mock_client.beta.files.upload.call_args[1]
        assert "file" in call_args
        assert call_args["file"][0] == "test.txt"
        assert call_args["file"][2] == "text/plain"


def test_upload_file_unknown_mime_type():
    """Test file upload falls back to application/octet-stream if mime type is unknown."""
    mock_client = MagicMock()
    mock_upload_result = MagicMock()
    mock_client.beta.files.upload.return_value = mock_upload_result

    with patch("html2md.upload.Path.exists", return_value=True), patch(
        "html2md.upload.mimetypes.guess_type", return_value=(None, None)
    ), patch("html2md.upload.anthropic.Anthropic", return_value=mock_client), patch(
        "html2md.upload.Path.open", mock_open(read_data=b"test data")
    ), patch(
        "html2md.upload.Path.name", "test.unknown", create=True
    ):

        result = upload_file("test.unknown")

        assert result == mock_upload_result
        mock_client.beta.files.upload.assert_called_once()
        call_args = mock_client.beta.files.upload.call_args[1]
        assert call_args["file"][2] == "application/octet-stream"


def test_main_success(capsys):
    """Test main function success path."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    with patch("html2md.upload.upload_file", return_value=mock_result):
        exit_code = main(["test.txt"])

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_123" in captured.out


def test_main_file_not_found(capsys):
    """Test main function handling FileNotFoundError."""
    with patch(
        "html2md.upload.upload_file",
        side_effect=FileNotFoundError("File not found: test.txt"),
    ):
        exit_code = main(["test.txt"])

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Error: File not found: test.txt" in captured.err


def test_main_api_error(capsys):
    """Test main function handling anthropic.APIError."""
    # Create a mock request object required by APIError
    mock_request = MagicMock()
    error = anthropic.APIError("API connection failed", request=mock_request, body=None)

    with patch("html2md.upload.upload_file", side_effect=error):
        exit_code = main(["test.txt"])

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "API error: API connection failed" in captured.err
