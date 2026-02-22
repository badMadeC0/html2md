"""Tests for upload functionality."""
import io
import sys
from unittest.mock import MagicMock, patch

# Mock anthropic module if not installed
try:
    import anthropic
except ImportError:
    anthropic = MagicMock()

    class APIError(Exception):
        pass

    anthropic.APIError = APIError
    anthropic.Anthropic = MagicMock()
    sys.modules["anthropic"] = anthropic

from html2md import upload


@patch("html2md.upload.anthropic.Anthropic")
@patch("pathlib.Path.open")
@patch("pathlib.Path.exists")
@patch("mimetypes.guess_type")
def test_upload_file_success(mock_guess_type, mock_exists, mock_open, mock_anthropic):
    """Test successful file upload."""
    mock_exists.return_value = True
    mock_guess_type.return_value = ("text/plain", None)

    mock_file_handle = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file_handle

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    mock_result = MagicMock()
    mock_result.id = "file_12345"
    mock_client.beta.files.upload.return_value = mock_result

    result = upload.upload_file("test_file.txt")

    mock_exists.assert_called_once()
    mock_guess_type.assert_called_once_with("test_file.txt")
    mock_client.beta.files.upload.assert_called_once()
    assert result == mock_result

    # Verify arguments passed to upload
    call_args = mock_client.beta.files.upload.call_args
    assert call_args is not None
    assert "file" in call_args.kwargs
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[0] == "test_file.txt"
    assert uploaded_file_tuple[1] == mock_file_handle
    assert uploaded_file_tuple[2] == "text/plain"


@patch("pathlib.Path.exists")
def test_upload_file_not_found(mock_exists):
    """Test file not found error."""
    mock_exists.return_value = False

    try:
        upload.upload_file("non_existent_file.txt")
    except FileNotFoundError:
        pass
    else:
        assert False, "Should have raised FileNotFoundError"


@patch("html2md.upload.anthropic.Anthropic")
@patch("pathlib.Path.open")
@patch("pathlib.Path.exists")
@patch("mimetypes.guess_type")
def test_upload_file_default_mime_type(
    mock_guess_type, mock_exists, mock_open, mock_anthropic
):
    """Test default mime type when detection fails."""
    mock_exists.return_value = True
    mock_guess_type.return_value = (None, None)

    mock_file_handle = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file_handle

    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client

    upload.upload_file("unknown_file")

    mock_client.beta.files.upload.assert_called_once()
    call_args = mock_client.beta.files.upload.call_args
    assert call_args.kwargs["file"][2] == "application/octet-stream"


@patch("html2md.upload.upload_file")
@patch("sys.stdout", new_callable=io.StringIO)
def test_main_success(mock_stdout, mock_upload_file):
    """Test successful execution of main."""
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_upload_file.return_value = mock_result

    ret = upload.main(["test_file.txt"])

    assert ret == 0
    mock_upload_file.assert_called_once_with("test_file.txt")
    assert "File uploaded successfully. ID: file_123" in mock_stdout.getvalue()


@patch("html2md.upload.upload_file")
@patch("sys.stderr", new_callable=io.StringIO)
def test_main_file_not_found(mock_stderr, mock_upload_file):
    """Test main handling of FileNotFoundError."""
    mock_upload_file.side_effect = FileNotFoundError("File not found: bad_file.txt")

    ret = upload.main(["bad_file.txt"])

    assert ret == 1
    assert "Error: File not found: bad_file.txt" in mock_stderr.getvalue()


@patch("html2md.upload.upload_file")
@patch("sys.stderr", new_callable=io.StringIO)
def test_main_api_error(mock_stderr, mock_upload_file):
    """Test main handling of Anthropic APIError."""
    from html2md.upload import anthropic as module_anthropic

    class TestAPIError(Exception):
        pass

    module_anthropic.APIError = TestAPIError
    mock_upload_file.side_effect = TestAPIError("API Error occurred")
    ret = upload.main(["test_file.txt"])

    assert ret == 1
    assert "API error:" in mock_stderr.getvalue()
