"""Tests for the upload module."""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure src is in sys.path if not running as package
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Mock anthropic if not installed
try:
    import anthropic
except ImportError:
    # Create a mock module structure that mimics what's needed
    anthropic = MagicMock()
    # Need to make sure APIError is available as a class we can instantiate or inherit from
    # But since we use it in exceptions, it needs to be a type.
    class MockAPIError(Exception):
        def __init__(self, message, request, body):
            super().__init__(message)
            self.message = message
            self.request = request
            self.body = body

    anthropic.APIError = MockAPIError
    anthropic.Anthropic = MagicMock()

    sys.modules["anthropic"] = anthropic

from html2md.upload import main, upload_file

@pytest.fixture
def mock_anthropic():
    # If anthropic was mocked in sys.modules, patch might behave interestingly if we use the string path.
    # But "html2md.upload.anthropic.Anthropic" should resolve to our mock or the real one.
    with patch("html2md.upload.anthropic.Anthropic") as mock:
        yield mock

def test_upload_file_success(tmp_path, mock_anthropic):
    """Test successful file upload."""
    # Create dummy file
    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    # Mock the client return value
    mock_client = mock_anthropic.return_value
    mock_client.beta.files.upload.return_value = MagicMock(id="file_123")

    result = upload_file(str(file_path))

    # Verify result
    assert result.id == "file_123"

    # Verify API call
    mock_client.beta.files.upload.assert_called_once()
    call_args = mock_client.beta.files.upload.call_args
    assert call_args is not None
    kwargs = call_args[1]
    assert "file" in kwargs

    filename, file_obj, mime_type = kwargs["file"]
    assert filename == "test.txt"
    assert mime_type == "text/plain"
    # Verify file content was read
    assert file_obj.name == str(file_path)

def test_upload_file_not_found(tmp_path):
    """Test file not found error."""
    with pytest.raises(FileNotFoundError):
        upload_file(str(tmp_path / "nonexistent.txt"))

def test_upload_file_mime_guessing(tmp_path, mock_anthropic):
    """Test MIME type guessing logic."""
    # Test with .json file
    json_file = tmp_path / "data.json"
    json_file.write_text("{}", encoding="utf-8")

    upload_file(str(json_file))

    mock_client = mock_anthropic.return_value
    args, kwargs = mock_client.beta.files.upload.call_args
    filename, _, mime_type = kwargs["file"]
    assert filename == "data.json"
    assert mime_type == "application/json"

def test_upload_file_mime_default(tmp_path, mock_anthropic):
    """Test default MIME type for unknown extension."""
    unknown_file = tmp_path / "data.unknown_ext_123"
    unknown_file.write_bytes(b"data")

    upload_file(str(unknown_file))

    mock_client = mock_anthropic.return_value
    args, kwargs = mock_client.beta.files.upload.call_args
    _, _, mime_type = kwargs["file"]
    assert mime_type == "application/octet-stream"

def test_main_success(capsys, monkeypatch):
    """Test successful CLI execution."""
    mock_upload = MagicMock()
    mock_upload.return_value.id = "file_123"
    monkeypatch.setattr("html2md.upload.upload_file", mock_upload)

    ret = main(["/path/to/file.txt"])

    assert ret == 0
    captured = capsys.readouterr()
    assert "File uploaded successfully. ID: file_123" in captured.out

    mock_upload.assert_called_once_with("/path/to/file.txt")

def test_main_file_not_found_cli(capsys, monkeypatch):
    """Test CLI handles FileNotFoundError."""
    mock_upload = MagicMock(side_effect=FileNotFoundError("Mocked file not found"))
    monkeypatch.setattr("html2md.upload.upload_file", mock_upload)

    ret = main(["/path/missing.txt"])

    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: Mocked file not found" in captured.err

def test_main_api_error_cli(capsys, monkeypatch):
    """Test CLI handles APIError."""
    # Create a mock APIError
    mock_request = MagicMock()
    # Need to make sure we use the anthropic.APIError that is being used in the code
    api_error = anthropic.APIError(message="Mocked API error", request=mock_request, body=None)

    mock_upload = MagicMock(side_effect=api_error)
    monkeypatch.setattr("html2md.upload.upload_file", mock_upload)

    ret = main(["/path/file.txt"])

    assert ret == 1
    captured = capsys.readouterr()
    assert "API error: Mocked API error" in captured.err
