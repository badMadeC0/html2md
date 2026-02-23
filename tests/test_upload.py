import sys
from unittest.mock import MagicMock, patch

# Mock anthropic module before importing html2md.upload
mock_anthropic = MagicMock()
sys.modules["anthropic"] = mock_anthropic

# Now we can import the module under test
from html2md.upload import upload_file


@patch("html2md.upload.Path")
@patch("html2md.upload.mimetypes")
def test_upload_file(mock_mimetypes, mock_path):
    # Setup
    file_path = "test_file.txt"
    mock_path_obj = MagicMock()
    mock_path.return_value = mock_path_obj
    mock_path_obj.exists.return_value = True
    mock_path_obj.name = "test_file.txt"
    mock_path_obj.__str__ = lambda s: file_path

    # Mock open context manager
    mock_file_handle = MagicMock()
    mock_path_obj.open.return_value.__enter__.return_value = mock_file_handle

    mock_mimetypes.guess_type.return_value = ("text/plain", None)

    # Mock Anthropic client
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client

    expected_result = MagicMock()
    mock_client.beta.files.upload.return_value = expected_result

    # Execute
    result = upload_file(file_path)

    # Verify
    assert result == expected_result
    mock_path.assert_called_once_with(file_path)
    mock_path_obj.exists.assert_called_once()
    mock_mimetypes.guess_type.assert_called_once_with(file_path)
    mock_anthropic.Anthropic.assert_called_once()
    mock_client.beta.files.upload.assert_called_once()

    # Verify arguments passed to upload
    call_args = mock_client.beta.files.upload.call_args
    assert call_args is not None
    assert "file" in call_args.kwargs
    uploaded_file_tuple = call_args.kwargs["file"]
    assert uploaded_file_tuple[0] == "test_file.txt"
    assert uploaded_file_tuple[1] == mock_file_handle
    assert uploaded_file_tuple[2] == "text/plain"


def test_upload_file_not_found():
    with patch("html2md.upload.Path") as mock_path:
        mock_path_obj = MagicMock()
        mock_path.return_value = mock_path_obj
        mock_path_obj.exists.return_value = False

        try:
            upload_file("nonexistent.txt")
        except FileNotFoundError:
            pass
        else:
            assert False, "Should have raised FileNotFoundError"
