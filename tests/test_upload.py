"""Tests for upload functionality."""
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock anthropic before import
mock_anthropic = MagicMock()
# Ensure APIError is an exception class we can raise/catch
class MockAPIError(Exception):
    pass
mock_anthropic.APIError = MockAPIError
sys.modules["anthropic"] = mock_anthropic

from html2md.upload import upload_file, main

def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding="utf-8")

    # Mock the client instance
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_client.beta.files.upload.return_value = mock_result

    result = upload_file(str(test_file))

    assert result.id == "file_123"
    mock_client.beta.files.upload.assert_called_once()

    # Verify arguments
    args, kwargs = mock_client.beta.files.upload.call_args
    file_tuple = kwargs['file']
    assert file_tuple[0] == "test.txt"  # filename
    # checking file content would require reading the file object passed
    assert file_tuple[2] == "text/plain"  # mimetype

def test_upload_file_not_found():
    """Test error raised when file not found."""
    with patch("pathlib.Path.exists", return_value=False):
        try:
            upload_file("nonexistent.txt")
        except FileNotFoundError as e:
            assert "File not found" in str(e)
        else:
            assert False, "Should have raised FileNotFoundError"

def test_upload_file_default_mime_type(tmp_path):
    """Test fallback to default mime type."""
    test_file = tmp_path / "test.unknown"
    test_file.write_text("content", encoding="utf-8")

    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    with patch("mimetypes.guess_type", return_value=(None, None)):
        upload_file(str(test_file))

    _, kwargs = mock_client.beta.files.upload.call_args
    assert kwargs['file'][2] == "application/octet-stream"

def test_main_success(capsys):
    """Test CLI main function success."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    with patch("html2md.upload.upload_file", return_value=mock_result):
        ret = main(["test.txt"])

    captured = capsys.readouterr()
    assert ret == 0
    assert "File uploaded successfully. ID: file_123" in captured.out

def test_main_file_not_found(capsys):
    """Test CLI handles FileNotFoundError."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Not found")):
        ret = main(["missing.txt"])

    captured = capsys.readouterr()
    assert ret == 1
    assert "Error: Not found" in captured.err

def test_main_api_error(capsys):
    """Test CLI handles API errors."""
    with patch("html2md.upload.upload_file", side_effect=mock_anthropic.APIError("API Error")):
        ret = main(["test.txt"])

    captured = capsys.readouterr()
    assert ret == 1
    assert "API error: API Error" in captured.err
