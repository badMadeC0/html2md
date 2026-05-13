import pytest
from unittest.mock import MagicMock, patch
from html2md import cli

@patch("requests.Session.get")
def test_xss_sanitization(mock_get, capsys, tmp_path):
    response = MagicMock()
    html = "<html><a href='javascript:alert(1)'>Click</a><img src='vbscript:msgbox(1)'></html>"
    response.iter_content.return_value = [html.encode("utf-8")]
    response.headers = {'Content-Length': str(len(html))}
    response.encoding = 'utf-8'
    mock_get.return_value = response

    cli.main(["--url", "http://example.com", "--outdir", str(tmp_path)])

    md_files = list(tmp_path.glob("*.md"))
    assert len(md_files) == 1
    content = md_files[0].read_text()

    assert "javascript:" not in content
    assert "vbscript:" not in content
    assert "(#)" in content
