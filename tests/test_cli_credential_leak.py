from unittest.mock import MagicMock, patch
import pytest
from html2md import cli
import io

@patch("requests.Session.get")
def test_cli_redacts_credentials_in_output(mock_get, capsys, tmp_path):
    outdir = tmp_path / "output"
    outdir.mkdir()

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    cli.main(["--url", "http://admin:secret123@example.com/foo", "--outdir", str(outdir)])
    outerr = capsys.readouterr()

    assert "admin:***@" in outerr.out
    assert "secret123" not in outerr.out

@patch("requests.Session.get")
def test_cli_redacts_credentials_in_errors(mock_get, tmp_path, capsys):
    outdir = tmp_path / "output"
    outdir.mkdir()

    import requests
    mock_get.side_effect = requests.RequestException("404 Client Error for url: http://admin:secret123@example.com/foo")

    cli.main(["--url", "http://admin:secret123@example.com/foo", "--outdir", str(outdir)])

    outerr = capsys.readouterr()
    output = outerr.err
    assert "admin:***@" in output
    assert "secret123" not in output
