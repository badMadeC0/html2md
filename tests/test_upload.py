"""Tests for upload functionality."""
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Define the exception class globally so it can be used for assertions
class MockAPIError(Exception):
    pass

@pytest.fixture
def mock_anthropic_module():
    """Create a mock anthropic module with required structure."""
    mock = MagicMock()
    mock.APIError = MockAPIError
    return mock

@pytest.fixture
def upload_module(mock_anthropic_module):
    """Import and return the html2md.upload module with patched anthropic."""
    with patch.dict(sys.modules, {"anthropic": mock_anthropic_module}):
        # If the module is already loaded, remove it to force re-import with patch
        if "html2md.upload" in sys.modules:
            del sys.modules["html2md.upload"]
        import html2md.upload
        # Force reload to pick up the mock
        import importlib
        importlib.reload(html2md.upload)
        yield html2md.upload

def test_upload_file_success(upload_module, mock_anthropic_module, tmp_path):
    """Test successful file upload."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding="utf-8")

    # Mock the client instance
    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_client.beta.files.upload.return_value = mock_result

    result = upload_module.upload_file(str(test_file))

    assert result.id == "file_123"
    mock_client.beta.files.upload.assert_called_once()

    # Verify arguments
    args, kwargs = mock_client.beta.files.upload.call_args
    file_tuple = kwargs['file']
    assert file_tuple[0] == "test.txt"  # filename
    assert file_tuple[2] == "text/plain"  # mimetype

def test_upload_file_not_found(upload_module):
    """Test error raised when file not found."""
    with patch("pathlib.Path.exists", return_value=False):
        try:
            upload_module.upload_file("nonexistent.txt")
        except FileNotFoundError as e:
            assert "File not found" in str(e)
        else:
            pytest.fail("Should have raised FileNotFoundError")

def test_upload_file_default_mime_type(upload_module, mock_anthropic_module, tmp_path):
    """Test fallback to default mime type."""
    test_file = tmp_path / "test.unknown"
    test_file.write_text("content", encoding="utf-8")

    mock_client = MagicMock()
    mock_anthropic_module.Anthropic.return_value = mock_client

    with patch("mimetypes.guess_type", return_value=(None, None)):
        upload_module.upload_file(str(test_file))

    _, kwargs = mock_client.beta.files.upload.call_args
    assert kwargs['file'][2] == "application/octet-stream"

def test_main_success(upload_module, capsys):
    """Test CLI main function success."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    # We patch the module directly since upload_module is the imported object
    with patch.object(upload_module, "upload_file", return_value=mock_result):
        ret = upload_module.main(["test.txt"])

    captured = capsys.readouterr()
    assert ret == 0
    assert "File uploaded successfully. ID: file_123" in captured.out

def test_main_file_not_found(upload_module, capsys):
    """Test CLI handles FileNotFoundError."""
    with patch.object(upload_module, "upload_file", side_effect=FileNotFoundError("Not found")):
        ret = upload_module.main(["missing.txt"])

    captured = capsys.readouterr()
    assert ret == 1
    assert "Error: Not found" in captured.err

def test_main_api_error(upload_module, mock_anthropic_module, capsys):
    """Test CLI handles API errors."""
    with patch.object(upload_module, "upload_file", side_effect=mock_anthropic_module.APIError("API Error")):
        ret = upload_module.main(["test.txt"])

    captured = capsys.readouterr()
    assert ret == 1
    assert "API error: API Error" in captured.err
