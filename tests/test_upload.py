"""Tests for upload CLI."""
import sys
from unittest.mock import MagicMock, patch

# Mock anthropic before importing upload
mock_anthropic = MagicMock()
class APIError(Exception):
    pass
mock_anthropic.APIError = APIError
sys.modules['anthropic'] = mock_anthropic

from html2md.upload import main


@patch("html2md.upload.upload_file")
def test_main_success(mock_upload_file, capsys):
    """Test successful execution of main."""
    mock_result = MagicMock()
    mock_result.id = "file_123"
    mock_upload_file.return_value = mock_result

    result = main(["test_file.txt"])

    assert result == 0
    mock_upload_file.assert_called_once_with("test_file.txt")

    captured = capsys.readouterr()
    assert "File uploaded successfully. ID: file_123\n" in captured.out
    assert captured.err == ""


@patch("html2md.upload.upload_file")
def test_main_file_not_found(mock_upload_file, capsys):
    """Test main when file is not found."""
    mock_upload_file.side_effect = FileNotFoundError("File not found: test_file.txt")

    result = main(["test_file.txt"])

    assert result == 1
    mock_upload_file.assert_called_once_with("test_file.txt")

    captured = capsys.readouterr()
    assert "Error: File not found: test_file.txt\n" in captured.err
    assert captured.out == ""


@patch("html2md.upload.upload_file")
def test_main_api_error(mock_upload_file, capsys):
    """Test main when API error occurs."""
    mock_upload_file.side_effect = mock_anthropic.APIError("API failed")

    result = main(["test_file.txt"])

    assert result == 1
    mock_upload_file.assert_called_once_with("test_file.txt")

    captured = capsys.readouterr()
    assert "API error: API failed\n" in captured.err
    assert captured.out == ""
