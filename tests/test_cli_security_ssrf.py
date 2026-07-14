import pytest
from unittest.mock import patch
from html2md import cli

@patch("requests.Session.get")
def test_ssrf_protection_blocks_localhost(mock_get, capsys, tmp_path):
    ret = cli.main(["--url", "http://localhost:8080/secret", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert ret == 1
    assert "SSRF protection" in outerr.err or "internal" in outerr.err.lower()
    mock_get.assert_not_called()

@patch("requests.Session.get")
def test_ssrf_protection_blocks_private_ip(mock_get, capsys, tmp_path):
    ret = cli.main(["--url", "http://192.168.1.1/admin", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert ret == 1
    assert "SSRF protection" in outerr.err
    mock_get.assert_not_called()
