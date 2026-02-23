"""Tests for the upload module."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Handle optional anthropic dependency for test environment
try:
    import anthropic
except ImportError:
    # Use a dummy class for type checking / mocking if the library is missing
    class MockAnthropic:
        class APIError(Exception):
            def __init__(self, message, request=None, body=None):
                super().__init__(message)
        class Anthropic:
            pass

    sys.modules["anthropic"] = MockAnthropic
    import anthropic


from html2md.upload import main, upload_file


def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    test_file = tmp_path / "test_file.txt"
    test_file.write_text("test content", encoding="utf-8")

    mock_result = MagicMock()
    mock_result.id = "file_12345"

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = mock_anthropic_cls.return_value
        mock_client.beta.files.upload.return_value = mock_result

        result = upload_file(str(test_file))

        assert result.id == "file_12345"

        # Verify the upload call arguments
        mock_client.beta.files.upload.assert_called_once()
        call_args = mock_client.beta.files.upload.call_args
        assert "file" in call_args.kwargs

        filename, file_obj, mime_type = call_args.kwargs["file"]
        assert filename == "test_file.txt"
        assert mime_type == "text/plain"
        # Check file name instead of reading closed file
        assert file_obj.name == str(test_file)


def test_upload_file_not_found():
    """Test uploading a non-existent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")


def test_upload_file_mime_type_guessing(tmp_path):
    """Test MIME type guessing logic."""
    # JSON file
    json_file = tmp_path / "data.json"
    json_file.write_text("{}", encoding="utf-8")

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = mock_anthropic_cls.return_value
        upload_file(str(json_file))

        call_args = mock_client.beta.files.upload.call_args
        _, _, mime_type = call_args.kwargs["file"]
        assert mime_type == "application/json"

    # Unknown extension
    unknown_file = tmp_path / "data.unknown_ext"
    unknown_file.write_bytes(b"data")

    with patch("anthropic.Anthropic") as mock_anthropic_cls:
        mock_client = mock_anthropic_cls.return_value
        upload_file(str(unknown_file))

        call_args = mock_client.beta.files.upload.call_args
        _, _, mime_type = call_args.kwargs["file"]
        assert mime_type == "application/octet-stream"


def test_main_success(tmp_path, capsys):
    """Test main function success path."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    mock_result = MagicMock()
    mock_result.id = "file_abc"

    with patch("html2md.upload.upload_file", return_value=mock_result) as mock_upload:
        # Pass positional argument, not --file
        ret = main([str(test_file)])

        assert ret == 0
        mock_upload.assert_called_once_with(str(test_file))

        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_abc" in captured.out


def test_main_file_not_found(capsys):
    """Test main function handling FileNotFoundError."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Mocked error")):
        # Pass positional argument
        ret = main(["bad_path.txt"])

        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: Mocked error" in captured.err


def test_main_api_error(tmp_path, capsys):
    """Test main function handling anthropic.APIError."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Create an APIError instance.
    # If anthropic is mocked above, we control it.
    # If anthropic is real, we need to respect its signature.
    # We'll try to instantiate it in a way that works for both if possible,
    # or just Mock the class if it's imported from the module.

    # Better yet, since we are patching upload_file, we can side_effect with ANY exception object.
    # But it must be an instance of anthropic.APIError for the except block to catch it.

    # We can patch anthropic.APIError in the module under test to be a standard Exception
    # to avoid signature issues.

    with patch("html2md.upload.anthropic.APIError", new=Exception):
        # Now the code will catch Exception (as anthropic.APIError)
        with patch("html2md.upload.upload_file", side_effect=Exception("API failure")):
            ret = main([str(test_file)])

            assert ret == 1
            captured = capsys.readouterr()
            # The code prints "API error: {exc}"
            assert "API error: API failure" in captured.err
