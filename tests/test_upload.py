"""Tests for upload functionality."""
import sys
from unittest.mock import MagicMock, patch
import pytest

# Mock anthropic before importing the module under test
# This is necessary because anthropic might not be installed in the test environment
sys.modules["anthropic"] = MagicMock()

from html2md.upload import upload_file

def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    # Setup
    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

    # Mock anthropic client instance and upload method
    mock_client = MagicMock()
    mock_upload = MagicMock()
    mock_client.beta.files.upload = mock_upload
    mock_upload.return_value.id = "file_123"

    with patch("html2md.upload.anthropic.Anthropic", return_value=mock_client) as mock_anthropic_class:
        # We also mock mimetypes to ensure deterministic behavior across environments
        with patch("html2md.upload.mimetypes.guess_type", return_value=("text/plain", None)):
            # Execute
            result = upload_file(str(file_path))

            # Verify
            assert result.id == "file_123"
            mock_anthropic_class.assert_called_once()
            mock_upload.assert_called_once()

            # Check arguments passed to upload
            call_args = mock_upload.call_args
            assert call_args is not None
            kwargs = call_args.kwargs
            assert "file" in kwargs
            file_tuple = kwargs["file"]
            assert file_tuple[0] == "test.txt"
            assert file_tuple[1].mode == "rb"
            assert file_tuple[2] == "text/plain"

def test_upload_file_not_found():
    """Test upload with non-existent file."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")

def test_upload_file_mime_type_fallback(tmp_path):
    """Test fallback mime type for unknown extensions."""
    # Setup a file with unknown extension
    file_path = tmp_path / "test.unknown"
    file_path.write_text("content", encoding="utf-8")

    mock_client = MagicMock()
    mock_upload = MagicMock()
    mock_client.beta.files.upload = mock_upload

    # Force mimetypes.guess_type to return None to simulate unknown type
    with patch("html2md.upload.mimetypes.guess_type", return_value=(None, None)):
        with patch("html2md.upload.anthropic.Anthropic", return_value=mock_client):
            # Execute
            upload_file(str(file_path))

            # Verify mime type fallback
            call_args = mock_upload.call_args
            kwargs = call_args[1]
            file_tuple = kwargs["file"]
            assert file_tuple[2] == "application/octet-stream"
