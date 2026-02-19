"""Tests for upload functionality."""
from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch
import pytest
from html2md.upload import upload_file

def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    # Setup
    file_path = tmp_path / "test.txt"
    file_path.write_text("content", encoding="utf-8")

mock_client, mock_upload = anthropic_mock_setup
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
"""Tests for upload functionality."""\nimport sys\nfrom unittest.mock import MagicMock, patch\nimport pytest\n\n# Mock anthropic before importing the module under test\n# This is necessary because anthropic might not be installed in the test environment.\n# The previous global sys.modules mock was removed, but for the test file to function\n# correctly and allow mocking of anthropic.APIError, we need to ensure 'anthropic'\n# is present in sys.modules as a MagicMock before 'html2md.upload' is imported.\n# This ensures that 'html2md.upload' can import 'anthropic' successfully, and\n# 'anthropic.APIError' can be defined on this mock for testing purposes.\nsys.modules["anthropic"] = MagicMock(APIError=type("APIError", (Exception,), {}))\n\nfrom html2md.upload import upload_file\n\ndef test_upload_file_success(tmp_path):\n    """Test successful file upload."""\n    # Setup\n    file_path = tmp_path / "test.txt"\n    file_path.write_text("content", encoding="utf-8")\n\n    # Mock anthropic client instance and upload method\n    mock_client = MagicMock()\n    mock_upload = MagicMock()\n    mock_client.beta.files.upload = mock_upload\n    mock_upload.return_value.id = "file_123"\n\n    with patch("html2md.upload.anthropic.Anthropic", return_value=mock_client) as mock_anthropic_class:\n        # We also mock mimetypes to ensure deterministic behavior across environments\n        with patch("html2md.upload.mimetypes.guess_type", return_value=("text/plain", None)):\n            # Execute\n            result = upload_file(str(file_path))\n\n            # Verify\n            assert result.id == "file_123"\n            mock_anthropic_class.assert_called_once()\n            mock_upload.assert_called_once()\n\n            # Check arguments passed to upload\n            call_args = mock_upload.call_args\n            assert call_args is not None\n            kwargs = call_args.kwargs\n            assert "file" in kwargs\n            file_tuple = kwargs["file"]\n            assert file_tuple[0] == "test.txt"\n            assert file_tuple[1].mode == "rb"\n            assert file_tuple[2] == "text/plain"\n\ndef test_upload_file_not_found():\n    """Test upload with non-existent file."""\n    with pytest.raises(FileNotFoundError):\n        upload_file("non_existent_file.txt")\n\ndef test_upload_file_mime_type_fallback(tmp_path):\n    """Test fallback mime type for unknown extensions."""\n    # Setup a file with unknown extension\n    file_path = tmp_path / "test.unknown"\n    file_path.write_text("content", encoding="utf-8")\n\n    mock_client = MagicMock()\n    mock_upload = MagicMock()\n    mock_client.beta.files.upload = mock_upload\n\n    # Force mimetypes.guess_type to return None to simulate unknown type\n    with patch("html2md.upload.mimetypes.guess_type", return_value=(None, None)):\n        with patch("html2md.upload.anthropic.Anthropic", return_value=mock_client):\n            # Execute\n            upload_file(str(file_path))\n\n            # Verify mime type fallback\n            call_args = mock_upload.call_args\n            kwargs = call_args[1]\n            file_tuple = kwargs["file"]\n            assert file_tuple[2] == "application/octet-stream"\n\ndef test_upload_file_api_error(tmp_path):\n    """Test upload_file propagates anthropic.APIError."""\n    file_path = tmp_path / "error.txt"\n    file_path.write_text("error content", encoding="utf-8")\n\n    mock_client = MagicMock()\n    mock_upload = MagicMock()\n    # Use the APIError defined on the mocked anthropic module in sys.modules\n    mock_upload.side_effect = sys.modules["anthropic"].APIError("API call failed")\n    mock_client.beta.files.upload = mock_upload\n\n    with patch("html2md.upload.anthropic.Anthropic", return_value=mock_client) as mock_anthropic_class:\n        with pytest.raises(sys.modules["anthropic"].APIError):\n            upload_file(str(file_path))\n\n        mock_anthropic_class.assert_called_once()\n        mock_upload.assert_called_once()
