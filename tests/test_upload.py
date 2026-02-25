"""Tests for the upload module."""

import os
import subprocess
import sys
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from html2md.upload import main, upload_file


def test_upload_file_success(tmp_path):
    """Test successful file upload."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("content", encoding="utf-8")

    mock_client_instance = MagicMock()
    mock_upload_response = MagicMock()
    mock_upload_response.id = "file_123"
    mock_client_instance.beta.files.upload.return_value = mock_upload_response

    with patch("anthropic.Anthropic", return_value=mock_client_instance) as mock_anthropic_class:
        result = upload_file(str(test_file))

        assert result.id == "file_123"
        mock_anthropic_class.assert_called_once()

        mock_client_instance.beta.files.upload.assert_called_once()
        call_kwargs = mock_client_instance.beta.files.upload.call_args.kwargs
        assert "file" in call_kwargs

        file_tuple = call_kwargs["file"]
        assert len(file_tuple) == 3
        assert file_tuple[0] == "test.txt"
        assert file_tuple[1].closed
        assert file_tuple[2] == "text/plain"


def test_upload_file_not_found():
    """Test upload_file raises FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        upload_file("non_existent_file.txt")


def test_upload_file_default_mime_type(tmp_path):
    """Test that DEFAULT_MIME_TYPE is used when mime type cannot be guessed."""
    from html2md.upload import DEFAULT_MIME_TYPE

    test_file = tmp_path / "test.unknown"
    test_file.write_text("content", encoding="utf-8")

    mock_client_instance = MagicMock()
    mock_client_instance.beta.files.upload.return_value = MagicMock()

    with patch("mimetypes.guess_type", return_value=(None, None)) as mock_guess_type, patch(
        "anthropic.Anthropic", return_value=mock_client_instance
    ):
        upload_file(str(test_file))

        mock_guess_type.assert_called_once_with(str(test_file))

        mock_client_instance.beta.files.upload.assert_called_once()
        call_kwargs = mock_client_instance.beta.files.upload.call_args.kwargs
        file_tuple = call_kwargs["file"]
        assert file_tuple[0] == "test.unknown"
        assert file_tuple[2] == DEFAULT_MIME_TYPE


def test_main_success(capsys):
    """Test main function successful execution."""
    mock_result = MagicMock()
    mock_result.id = "file_123"

    with patch("html2md.upload.upload_file", return_value=mock_result) as mock_upload:
        ret = main(["test.txt"])

        assert ret == 0
        mock_upload.assert_called_once_with("test.txt")

        captured = capsys.readouterr()
        assert "File uploaded successfully. ID: file_123" in captured.out


def test_main_file_not_found_error(capsys):
    """Test main function handles FileNotFoundError gracefully."""
    with patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Missing file")):
        ret = main(["missing.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        assert captured.err.strip() == "Error: Missing file"


def test_main_api_error(capsys):
    """Test main function handles APIError gracefully."""
    error_instance = anthropic.APIError.__new__(anthropic.APIError)
    error_instance.args = ("Something went wrong with API",)
    error_instance.message = "Something went wrong with API"

    with patch("html2md.upload.upload_file", side_effect=error_instance):
        ret = main(["test.txt"])

        assert ret == 1

        captured = capsys.readouterr()
        assert captured.err.strip() == "Error: Something went wrong with API"


def test_main_no_args(capsys):
    """Test main function exits when no file is provided."""
    with pytest.raises(SystemExit) as excinfo:
        main([])

    assert excinfo.value.code != 0

    captured = capsys.readouterr()
    assert "usage: html2md-upload" in captured.err


def test_upload_help_runs():
    """Verify html2md-upload --help exits with code 0."""
    env = os.environ.copy()
    src_path = os.path.join(os.getcwd(), "src")
    env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)

    result = subprocess.run(
        [sys.executable, "-m", "html2md.upload", "--help"],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    assert result.returncode == 0
    assert "usage: html2md-upload" in result.stdout
