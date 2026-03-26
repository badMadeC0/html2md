"""Security tests for SSRF protection."""

import pytest
from unittest.mock import patch, MagicMock
from html2md import cli


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost/admin",
        "http://127.0.0.1/server-status",
        "http://169.254.169.254/latest/meta-data/",
        "http://[::1]/",
        "http://10.0.0.1/internal",
        "http://192.168.1.1/config",
        "http://172.16.0.5/api",
    ],
)
@patch("requests.Session.get")
def test_ssrf_protection_blocks_local_ips(mock_get, capsys, tmp_path, url):
    """Local, private, and reserved IPs must be blocked to prevent SSRF."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    cli.main(["--url", url, "--outdir", str(outdir)])
    outerr = capsys.readouterr()

    assert "Error: URL resolves to a local or private network address" in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_ssrf_protection_allows_public_ips(mock_get, capsys, tmp_path):
    """Public, safe IPs should be allowed."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    response = MagicMock()
    response.text = "<h1>safe</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    url = "http://example.com/safe"
    cli.main(["--url", url, "--outdir", str(outdir)])
    outerr = capsys.readouterr()

    assert "Success!" in outerr.out
    mock_get.assert_called_once()
