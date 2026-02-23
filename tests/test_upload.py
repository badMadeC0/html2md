"""Tests for the upload module."""
import importlib
import os
import subprocess
import sys
from unittest.mock import MagicMock, patch
import pytest

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def mock_anthropic_upload_module():
    """Provide upload module with anthropic mocked, restoring state afterwards."""
    mock_anthropic = MagicMock()

    class MockAPIError(Exception):
        pass

    mock_anthropic.APIError = MockAPIError

    with patch.dict(sys.modules, {"anthropic": mock_anthropic}):
        import html2md.upload
        importlib.reload(html2md.upload)
        yield html2md.upload, MockAPIError


def test_upload_file_not_found(mock_anthropic_upload_module):
    """Test that FileNotFoundError is raised when file does not exist."""
    upload_module, _ = mock_anthropic_upload_module
    with pytest.raises(FileNotFoundError):
        upload_module.upload_file("non_existent_file.txt")


def test_main_file_not_found(capsys, mock_anthropic_upload_module):
    """Test main function when file does not exist."""
    upload_module, _ = mock_anthropic_upload_module
    with patch.object(upload_module, "upload_file", side_effect=FileNotFoundError("File not found")):
        exit_code = upload_module.main(["non_existent.txt"])
        assert exit_code == 1


def test_main_success(capsys, mock_anthropic_upload_module):
    """Test main function on successful upload."""
    upload_module, _ = mock_anthropic_upload_module
    mock_result = MagicMock()
    mock_result.id = "file_123"
    with patch.object(upload_module, "upload_file", return_value=mock_result):
        exit_code = upload_module.main(["test.txt"])
        assert exit_code == 0


def test_main_api_error(capsys, mock_anthropic_upload_module):
    """Test main function on API error."""
    upload_module, MockAPIError = mock_anthropic_upload_module
    with patch.object(upload_module, "upload_file", side_effect=MockAPIError("API error")):
        exit_code = upload_module.main(["test.txt"])
        assert exit_code == 1


def test_html2md_upload_help_runs():
    """Verify that 'html2md-upload --help' runs and exits with code 0."""
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    if existing_pythonpath:
        env["PYTHONPATH"] = src_path + os.pathsep + existing_pythonpath
    else:
        env["PYTHONPATH"] = src_path
    result = subprocess.run(
        [sys.executable, "-m", "html2md.upload", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower()
