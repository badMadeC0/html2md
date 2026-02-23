"""Tests for the upload module."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure anthropic is importable even if not installed (for testing logic)
try:
    import anthropic
except ImportError:
    # If anthropic is not installed, mock it
    anthropic = MagicMock()
    # Mock APIError as an exception class so it can be caught
    class MockAPIError(Exception):
        def __init__(self, message, request=None, body=None):
            super().__init__(message)
            self.message = message
            self.request = request
            self.body = body

    anthropic.APIError = MockAPIError
    sys.modules["anthropic"] = anthropic

# Now import the module under test
# We rely on PYTHONPATH=src being set when running tests
from html2md.upload import main, upload_file

def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    # Create a dummy file
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding="utf-8")

    # Mock the anthropic client
    with patch("html2md.upload.anthropic.Anthropic") as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_upload_method = mock_client.beta.files.upload
        mock_upload_method.return_value.id = "file_123"

        result = upload_file(str(test_file))

        assert result.id == "file_123"

        # Verify call arguments
        mock_upload_method.assert_called_once()
        args, kwargs = mock_upload_method.call_args
        uploaded_file_tuple = kwargs['file']
        assert uploaded_file_tuple[0] == "test.txt"
        # Verify mime type
        assert uploaded_file_tuple[2] == "text/plain"

def test_upload_file_not_found():
    """Test upload with non-existent file."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")

def test_upload_file_mime_type_guessing(tmp_path):
    """Test mime type guessing logic."""
    # Test unknown extension
    unknown_file = tmp_path / "test.unknown"
    unknown_file.write_text("content", encoding="utf-8")

    with patch("html2md.upload.anthropic.Anthropic") as MockAnthropic:
        mock_client = MockAnthropic.return_value
        mock_upload = mock_client.beta.files.upload

        upload_file(str(unknown_file))

        # Verify default mime type
        args, kwargs = mock_upload.call_args
        assert kwargs['file'][2] == "application/octet-stream"

def test_main_success(tmp_path, capsys):
    """Test main function success path."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    with patch("html2md.upload.upload_file") as mock_upload:
        mock_upload.return_value.id = "file_123"

        # 'file' is a positional argument
        ret = main([str(test_file)])

        assert ret == 0
        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_123" in captured.out
        mock_upload.assert_called_once_with(str(test_file))

def test_main_file_not_found(capsys):
    """Test main function handles FileNotFoundError."""
    # We don't need a real file if we mock upload_file to fail
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("oops")):
        ret = main(["bad_path.txt"])

        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: oops" in captured.err

def test_main_api_error(tmp_path, capsys):
    """Test main function handles APIError."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Simulate API error
    # We need an instance of the class that html2md.upload uses as anthropic.APIError

    # Check if we are using the real anthropic or the mock
    try:
        # Use the actual class from the imported module (whether real or mock)
        APIErrorClass = anthropic.APIError
    except AttributeError:
        # Should not happen given our setup
        APIErrorClass = Exception

    # Create exception instance
    # If it's the real one, it needs args. If mock, it might need args depending on our mock class.
    # Our MockAPIError takes message, request, body.
    # Real APIError takes message, request, body=None.

    mock_request = MagicMock()
    try:
        api_error = APIErrorClass(message="API Failed", request=mock_request, body={})
    except TypeError:
         # Fallback if signature doesn't match
         api_error = APIErrorClass("API Failed")

    with patch("html2md.upload.upload_file", side_effect=api_error):
        ret = main([str(test_file)])

        assert ret == 1
        captured = capsys.readouterr()
        # The error message printed depends on str(exc)
        # Check for key parts
        assert "API error:" in captured.err
        assert "API Failed" in captured.err
