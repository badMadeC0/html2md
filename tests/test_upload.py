"""Tests for the upload module."""
import subprocess
import sys
from unittest.mock import MagicMock, patch
import pytest

import anthropic

from html2md.upload import main, upload_file

def test_upload_file_success(tmp_path):
    """Deprecated duplicate of test_upload_file_success; kept empty to avoid redefinition issues."""
    # This function body is intentionally left empty because a later
    # definition of test_upload_file_success in this module supersedes it.
    # Keeping only a pass statement avoids multiple-assignments before use.
    pass


def test_upload_file_not_found():
    """Deprecated duplicate of test_upload_file_not_found; kept empty to avoid redefinition issues."""
    # This function body is intentionally left empty because a later
    # definition of test_upload_file_not_found in this module supersedes it.
    # Keeping only a pass statement avoids multiple-assignments before use.
    pass
import pytest


def test_main_success(capsys):
    """Test main function successful execution."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    # We mock upload_file to isolate main logic
    with patch("html2md.upload.upload_file", return_value=mock_result) as mock_upload:
        # Mock sys.argv if needed, or pass arguments explicitly
        ret = main(["test.txt"])

        assert ret == 0
        mock_upload.assert_called_once_with("test.txt")

        captured = capsys.readouterr()
        # Check stdout for success message
        assert "File uploaded successfully. ID: file_123" in captured.out


def test_main_file_not_found_error(capsys):
    """Test main function handles FileNotFoundError gracefully."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Missing file")):
        ret = main(["missing.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        # Check stderr for error message
        assert "Error: Missing file" in captured.err


def test_main_api_error(capsys):
    """Test main function handles APIError gracefully."""
    mock_request = MagicMock()
    error_instance = anthropic.APIError(message="Something went wrong with API", request=mock_request, body={})

    with patch("html2md.upload.upload_file", side_effect=error_instance):
        ret = main(["test.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        # Check stderr for error message
        assert "API error: Something went wrong with API" in captured.err

def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    # Create a temporary file
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding="utf-8")

    # Mock the client instance and its upload method
    mock_client_instance = MagicMock()
    mock_upload_response = MagicMock()
    mock_upload_response.id = "file_123"
    mock_client_instance.beta.files.upload.return_value = mock_upload_response

    # Patch the Anthropic class constructor to return our mock instance
    with patch("anthropic.Anthropic", return_value=mock_client_instance) as mock_anthropic_class:
        result = upload_file(str(test_file))

        # Verify result
        assert result.id == "file_123"

        # Verify Anthropic client was initialized
        mock_anthropic_class.assert_called_once()

        # Verify upload was called correctly
        mock_client_instance.beta.files.upload.assert_called_once()
        call_kwargs = mock_client_instance.beta.files.upload.call_args.kwargs
        assert "file" in call_kwargs

        # Check arguments passed to upload: (filename, file_obj, mime_type)
        file_tuple = call_kwargs["file"]
        assert len(file_tuple) == 3
        assert file_tuple[0] == "test.txt"
        # The file object is closed after the function returns, so we check it's closed now
        # verifying it was used in a context manager
        assert file_tuple[1].closed
        assert file_tuple[2] == "text/plain"


def test_upload_file_not_found():
    """Test upload_file raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")


def test_main_success(capsys):
    """Test main function successful execution."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    # We mock upload_file to isolate main logic
    with patch("html2md.upload.upload_file", return_value=mock_result) as mock_upload:
        # Mock sys.argv if needed, or pass arguments explicitly
        ret = main(["test.txt"])

        assert ret == 0
        mock_upload.assert_called_once_with("test.txt")

        captured = capsys.readouterr()
        # Check stdout for success message
        assert "File uploaded successfully. ID: file_123" in captured.out


def test_main_file_not_found_error(capsys):
    """Test main function handles FileNotFoundError gracefully."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Missing file")):
        ret = main(["missing.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        # Check stderr for error message
        assert "Error: Missing file" in captured.err


def test_main_api_error(capsys):
    """Test main function handles APIError gracefully."""
    # Use the mocked APIError class we defined earlier
    error_instance = MockAPIError("Something went wrong with API")

    with patch("html2md.upload.upload_file", side_effect=error_instance):
        ret = main(["test.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        # Check stderr for error message
        assert "Error:" in captured.err

def test_main_no_args(capsys):
    """Test main function exits when no file is provided."""
    with pytest.raises(SystemExit) as excinfo:
        main([])
    
    assert excinfo.value.code != 0

    captured = capsys.readouterr()
    assert "usage: html2md-upload" in captured.err


def test_upload_help_runs():
    """Verify html2md-upload --help exits with code 0."""
    result = subprocess.run(
        [sys.executable, "-m", "html2md.upload", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "usage: html2md-upload" in result.stdout
