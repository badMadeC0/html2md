"""Tests for the upload module."""

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest


class MockAPIError(Exception):
    """Test replacement for anthropic.APIError."""


@pytest.fixture
def upload_with_mock_anthropic():
    """Import upload module with a fresh mocked Anthropic SDK per test."""
    previous_upload_module = sys.modules.pop("html2md.upload", None)
    mock_anthropic = MagicMock()
    mock_anthropic.APIError = MockAPIError

    try:
        with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
            upload_module = importlib.import_module("html2md.upload")
            yield upload_module, mock_anthropic
    finally:
        sys.modules.pop("html2md.upload", None)
        if previous_upload_module is not None:
            sys.modules["html2md.upload"] = previous_upload_module


def test_upload_file_not_found(upload_with_mock_anthropic):
    """Test that upload_file raises FileNotFoundError for non-existent files."""
    upload_module, _ = upload_with_mock_anthropic

    with pytest.raises(FileNotFoundError, match="File not found:.*nonexistent.txt"):
        upload_module.upload_file("nonexistent.txt")


def test_upload_file_success_known_mime(tmp_path, upload_with_mock_anthropic):
    """Test successful upload with a known MIME type."""
    upload_module, mock_anthropic = upload_with_mock_anthropic

    # Create a temporary file
    test_file = tmp_path / "test.html"
    test_file.write_text("<html><body>Test</body></html>", encoding="utf-8")

    # Mock the client
    mock_client_instance = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client_instance
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_client_instance.beta.files.upload.return_value = mock_result

    # Call the function
    with patch.object(upload_module.mimetypes, "guess_type", return_value=("text/html", None)):
        result = upload_module.upload_file(str(test_file))

    # Verify result and client calls
    assert result == mock_result
    mock_anthropic.Anthropic.assert_called_once()
    mock_client_instance.beta.files.upload.assert_called_once()

    # Verify call arguments
    call_kwargs = mock_client_instance.beta.files.upload.call_args[1]
    assert "file" in call_kwargs
    file_tuple = call_kwargs["file"]
    assert file_tuple[0] == "test.html"
    assert hasattr(file_tuple[1], "read")  # Verify it's a file-like object
    assert file_tuple[2] == "text/html"  # Known MIME type


def test_upload_file_success_unknown_mime(tmp_path, upload_with_mock_anthropic):
    """Test successful upload falls back to application/octet-stream for unknown MIME."""
    upload_module, mock_anthropic = upload_with_mock_anthropic

    # Create a temporary file with an unknown extension
    test_file = tmp_path / "test.unknown_ext"
    test_file.write_text("Some random data", encoding="utf-8")

    # Mock the client
    mock_client_instance = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client_instance

    # Call the function
    with patch.object(upload_module.mimetypes, "guess_type", return_value=(None, None)):
        upload_module.upload_file(str(test_file))

    # Verify fallback MIME type
    call_kwargs = mock_client_instance.beta.files.upload.call_args[1]
    file_tuple = call_kwargs["file"]
    assert file_tuple[2] == "application/octet-stream"


def test_main_success(tmp_path, capsys, upload_with_mock_anthropic):
    """Test main CLI function on successful upload."""
    upload_module, mock_anthropic = upload_with_mock_anthropic

    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello", encoding="utf-8")

    mock_client_instance = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client_instance
    mock_client_instance.beta.files.upload.return_value.id = "file_456"

    # Call main
    ret = upload_module.main([str(test_file)])

    # Verify output and return code
    assert ret == 0
    captured = capsys.readouterr()
    assert "File uploaded successfully. ID: file_456" in captured.out


def test_main_file_not_found(capsys, upload_with_mock_anthropic):
    """Test main CLI function with non-existent file."""
    upload_module, _ = upload_with_mock_anthropic

    ret = upload_module.main(["nonexistent.txt"])

    # Verify output and return code
    assert ret == 1
    captured = capsys.readouterr()
    assert "Error: File not found:" in captured.err


def test_main_api_error(tmp_path, capsys, upload_with_mock_anthropic):
    """Test main CLI function when Anthropic API raises an error."""
    upload_module, mock_anthropic = upload_with_mock_anthropic

    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello", encoding="utf-8")

    mock_client_instance = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client_instance
    mock_client_instance.beta.files.upload.side_effect = MockAPIError("API failure")

    # Call main
    ret = upload_module.main([str(test_file)])

    # Verify output and return code
    assert ret == 1
    captured = capsys.readouterr()
    assert "API error: API failure" in captured.err
