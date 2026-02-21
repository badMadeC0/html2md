"""Tests for the upload module."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from html2md.upload import upload_file


def test_upload_file_calls_beta_api(tmp_path: Path):
    """Test that upload_file calls the beta API endpoint."""
    # Create a dummy file
    file_path = tmp_path / "test.txt"
    file_path.write_text("dummy content", encoding="utf-8")

    # Create a mock client
    mock_client = MagicMock()
    # Configure the return value for the upload method
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_client.beta.files.upload.return_value = mock_result

    # Call the function under test
    result = upload_file(str(file_path), client=mock_client)

    # Verify the result
    assert result == mock_result

    # Verify that the beta API was called
    mock_client.beta.files.upload.assert_called_once()

    # Inspect arguments
    call_kwargs = mock_client.beta.files.upload.call_args.kwargs
    assert "file" in call_kwargs
    file_tuple = call_kwargs["file"]
    # file_tuple structure: (filename, file_object, mime_type)
    assert file_tuple[0] == "test.txt"
    # Verify file object is open and readable
    assert file_tuple[1].name == str(file_path)
    assert file_tuple[2] == "text/plain"


def test_upload_file_not_found():
    """Test that upload_file raises FileNotFoundError for missing files."""
    with pytest.raises(FileNotFoundError):
        upload_file("nonexistent_file.txt")
