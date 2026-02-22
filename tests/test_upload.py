"""Tests for html2md.upload."""

import sys
from unittest.mock import MagicMock, patch

# Mock anthropic before importing html2md.upload as it is not installed in the environment
# This is required for the import to succeed.
if "anthropic" not in sys.modules:
    mock_anthropic = MagicMock()

    # Define APIError as an exception class so it can be caught
    class MockAPIError(Exception):
        def __init__(self, message, request=None, body=None):
            super().__init__(message)
            self.request = request
            self.body = body

    mock_anthropic.APIError = MockAPIError
    sys.modules["anthropic"] = mock_anthropic

from html2md.upload import upload_file, main


@patch("html2md.upload.anthropic")
def test_upload_file_no_client(mock_anthropic):
    """Test upload_file creates a new client when none is provided."""
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    # Mock path existence and open
    with patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.open", MagicMock()
    ):

        upload_file("dummy.txt")

        mock_anthropic.Anthropic.assert_called_once()
        mock_client.beta.files.upload.assert_called_once()


@patch("html2md.upload.anthropic")
def test_upload_file_with_client(mock_anthropic):
    """Test upload_file reuses the provided client."""
    mock_client = MagicMock()

    with patch("pathlib.Path.exists", return_value=True), patch(
        "pathlib.Path.open", MagicMock()
    ):

        upload_file("dummy.txt", client=mock_client)

        mock_anthropic.Anthropic.assert_not_called()
        mock_client.beta.files.upload.assert_called_once()


@patch("html2md.upload.anthropic")
@patch("html2md.upload.upload_file")
def test_main_passes_client(mock_upload_file, mock_anthropic):
    """Test that main creates and passes a client to upload_file."""
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    # Mock argv
    argv = ["dummy.txt"]

    with patch("sys.stdout", new_callable=MagicMock):
        main(argv)

    mock_anthropic.Anthropic.assert_called_once()
    mock_upload_file.assert_called_once_with("dummy.txt", client=mock_client)


def test_main_api_error(capsys):
    """Test that main handles anthropic.APIError correctly."""
    with patch("html2md.upload.upload_file") as mock_upload:
        # Get the mocked APIError class from the module
        mock_api_error = sys.modules["anthropic"].APIError
        mock_upload.side_effect = mock_api_error("Test API Error")

        # Call main with a dummy file argument
        ret = main(["dummy.txt"])

        # Verify return code is 1 (failure)
        assert ret == 1

        # Verify error message in stderr
        captured = capsys.readouterr()
        assert "API error: Test API Error" in captured.err


def test_main_file_not_found(capsys):
    """Test that main handles FileNotFoundError correctly."""
    with patch("html2md.upload.upload_file") as mock_upload:
        mock_upload.side_effect = FileNotFoundError("File not found")

        ret = main(["nonexistent.txt"])

        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err
