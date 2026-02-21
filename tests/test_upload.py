import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock anthropic module before importing html2md.upload
mock_anthropic = MagicMock()


class MockAPIError(Exception):
    def __init__(self, message, request=None, body=None):
        super().__init__(message)
        self.request = request
        self.body = body


mock_anthropic.APIError = MockAPIError
sys.modules["anthropic"] = mock_anthropic

# Now import the module under test
from html2md import upload


def test_upload_main_api_error(capsys):
    """Test that main handles anthropic.APIError correctly."""
    with patch("html2md.upload.upload_file") as mock_upload:
        # Simulate APIError
        mock_upload.side_effect = MockAPIError("Test API Error")

        # Call main with a dummy file argument
        ret = upload.main(["dummy.txt"])

        # Verify return code is 1 (failure)
        assert ret == 1

        # Verify error message in stderr
        captured = capsys.readouterr()
        assert "API error: Test API Error" in captured.err


def test_upload_main_file_not_found(capsys):
    """Test that main handles FileNotFoundError correctly."""
    with patch("html2md.upload.upload_file") as mock_upload:
        mock_upload.side_effect = FileNotFoundError("File not found")

        ret = upload.main(["nonexistent.txt"])

        assert ret == 1
        captured = capsys.readouterr()
        assert "Error: File not found" in captured.err


def test_upload_main_success(capsys):
    """Test that main handles successful upload correctly."""
    with patch("html2md.upload.upload_file") as mock_upload:
        mock_result = MagicMock()
        mock_result.id = "file_12345"
        mock_upload.return_value = mock_result

        ret = upload.main(["valid.txt"])

        assert ret == 0
        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_12345" in captured.out


def test_upload_file_success(tmp_path):
    """Test the upload_file function logic."""
    # Create a dummy file
    test_file = tmp_path / "test.txt"
    test_file.write_text("content")

    # Mock anthropic.Anthropic
    with patch("html2md.upload.anthropic.Anthropic") as mock_client_cls:
        mock_client = mock_client_cls.return_value
        mock_files = mock_client.beta.files
        mock_upload_resp = MagicMock()
        mock_upload_resp.id = "file_abc"
        mock_files.upload.return_value = mock_upload_resp

        result = upload.upload_file(str(test_file))

        assert result.id == "file_abc"
        mock_files.upload.assert_called_once()

        # Verify arguments passed to upload
        call_args = mock_files.upload.call_args
        assert call_args is not None
        kwargs = call_args.kwargs
        assert "file" in kwargs
        file_tuple = kwargs["file"]
        assert file_tuple[0] == "test.txt"
        assert file_tuple[2] == "text/plain"  # mimetypes should guess this


def test_upload_file_not_found():
    """Test upload_file raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        upload.upload_file("non_existent_file.txt")
