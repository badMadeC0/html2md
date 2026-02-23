"""Tests for the upload module."""
import pytest
import subprocess
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Mock anthropic for unit tests
mock_anthropic = MagicMock()
class MockAPIError(Exception):
    pass
mock_anthropic.APIError = MockAPIError
sys.modules["anthropic"] = mock_anthropic

from html2md.upload import upload_file, main

def test_upload_file_not_found():
    """Test that FileNotFoundError is raised when file does not exist."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")

def test_main_file_not_found(capsys):
    """Test main function when file does not exist."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("File not found")):
        exit_code = main(["non_existent.txt"])
        assert exit_code == 1

def test_main_success(capsys):
    """Test main function on successful upload."""
    mock_result = MagicMock()
    mock_result.id = "file_123"
    with patch("html2md.upload.upload_file", return_value=mock_result):
        exit_code = main(["test.txt"])
        assert exit_code == 0

def test_main_api_error(capsys):
    """Test main function on API error."""
    with patch("html2md.upload.upload_file", side_effect=MockAPIError("API error")):
        exit_code = main(["test.txt"])
        assert exit_code == 1


def test_html2md_upload_help_runs():
    """Verify that 'html2md-upload --help' runs and exits with code 0."""
    # This assumes 'html2md-upload' is a console script available in the PATH.
    # If it's not, the test might need to invoke the module directly, e.g.,
    # [sys.executable, "-m", "html2md.cli", "upload", "--help"]
    # or similar, depending on how the entry point is configured in pyproject.toml.
    result = subprocess.run(["html2md-upload", "--help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
