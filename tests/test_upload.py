from __future__ import annotations

import runpy
from unittest import mock

import pytest
import anthropic

from html2md.upload import upload_file, main


def test_upload_file_success(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy content")

    mock_client = mock.MagicMock()
    mock_result = mock.MagicMock()
    mock_result.id = "file_123"
    mock_client.beta.files.upload.return_value = mock_result

    with mock.patch("html2md.upload.anthropic.Anthropic", return_value=mock_client):
        result = upload_file(str(test_file))

    assert result == mock_result
    mock_client.beta.files.upload.assert_called_once()

    call_kwargs = mock_client.beta.files.upload.call_args[1]
    assert "file" in call_kwargs
    file_tuple = call_kwargs["file"]
    assert len(file_tuple) == 3
    assert file_tuple[0] == "test.txt"
    assert hasattr(file_tuple[1], "read")
    assert file_tuple[2] == "text/plain"


def test_upload_file_not_found():
    with pytest.raises(FileNotFoundError, match="File not found"):
        upload_file("nonexistent_file.txt")


def test_upload_file_unknown_mime_type(tmp_path):
    test_file = tmp_path / "test.unknown_ext"
    test_file.write_bytes(b"dummy content")

    mock_client = mock.MagicMock()

    with mock.patch("html2md.upload.anthropic.Anthropic", return_value=mock_client):
        with mock.patch("mimetypes.guess_type", return_value=(None, None)):
            upload_file(str(test_file))

    mock_client.beta.files.upload.assert_called_once()
    call_kwargs = mock_client.beta.files.upload.call_args[1]
    file_tuple = call_kwargs["file"]
    assert file_tuple[2] == "application/octet-stream"


def test_main_success(tmp_path, capsys):
    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy content")

    mock_result = mock.MagicMock()
    mock_result.id = "file_123"

    with mock.patch("html2md.upload.upload_file", return_value=mock_result):
        return_code = main([str(test_file)])

    assert return_code == 0
    captured = capsys.readouterr()
    assert "File uploaded successfully. ID: file_123" in captured.out


def test_main_file_not_found(capsys):
    with mock.patch("html2md.upload.upload_file", side_effect=FileNotFoundError("Mocked not found")):
        return_code = main(["nonexistent.txt"])

    assert return_code == 1
    captured = capsys.readouterr()
    assert "Error: Mocked not found" in captured.err


def test_main_api_error(tmp_path, capsys):
    test_file = tmp_path / "test.txt"
    test_file.write_text("dummy")

    api_error = anthropic.APIError(
        message="Mocked API error",
        request=mock.MagicMock(),
        body=None,
    )
    with mock.patch("html2md.upload.upload_file", side_effect=api_error):
        return_code = main([str(test_file)])

    assert return_code == 1
    captured = capsys.readouterr()
    assert "API error:" in captured.err
    assert "Mocked API error" in captured.err


def test_main_execution(tmp_path):
    missing_file = tmp_path / "nonexistent.txt"
    with mock.patch("sys.argv", ["html2md-upload", str(missing_file)]):
        with pytest.raises(SystemExit) as exc:
            runpy.run_module("html2md.upload", run_name="__main__")
        assert exc.value.code == 1
