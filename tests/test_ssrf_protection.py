"""Test SSRF protection."""
"""Test SSRF protection."""

from unittest.mock import patch, MagicMock
from html2md.cli import main, is_safe_url


def test_is_safe_url_public():
    """Test public URL."""
    """Test public URL."""
    # google.com should resolve to public IPs
    assert is_safe_url("https://google.com") is True
    assert is_safe_url("http://example.com/foo/bar") is True


def test_is_safe_url_private():
    """Test private URL."""
    """Test private URL."""
    # Localhost, 127.0.0.1 and other private IPs should be blocked
    assert is_safe_url("http://localhost/") is False
    assert is_safe_url("http://127.0.0.1:8080/admin") is False
    assert is_safe_url("http://192.168.1.1/") is False
    assert is_safe_url("http://10.0.0.5/") is False
    assert is_safe_url("http://169.254.169.254/latest/meta-data/") is False


def test_is_safe_url_invalid():
    """Test invalid URL."""
    """Test invalid URL."""
    # Invalid URLs or URLs without a hostname should return False
    assert is_safe_url("http://") is False
    assert is_safe_url("not_a_url") is False


@patch("requests.Session")
def test_main_blocks_private_ip(mock_session, capsys):
    """Test main blocks private IP."""
    """Test main blocks private IP."""
    # Call main with a private IP URL
    exit_code = main(["--url", "http://127.0.0.1:8000/"])

    assert exit_code == 1

    # Ensure requests was not called
    mock_session.return_value.get.assert_not_called()

    # Check stderr
    captured = capsys.readouterr()
    assert "resolves to a private or reserved IP address" in captured.err
    assert "SSRF protection" in captured.err


@patch("requests.Session")
@patch("html2md.cli.is_safe_url")
def test_main_allows_public_ip(mock_is_safe, mock_session, capsys):
    """Test main allows public IP."""
    """Test main allows public IP."""
    mock_is_safe.return_value = True

    # Mock response
    mock_resp = MagicMock()
    mock_resp.iter_content.return_value = [b"<html><body><h1>Test</h1></body></html>"]
    mock_resp.encoding = "utf-8"
    mock_resp.headers = {"Content-Length": "39"}
    mock_session.return_value.get.return_value = mock_resp

    exit_code = main(["--url", "http://example.com/"])

    assert exit_code == 0
    mock_session.return_value.get.assert_called_once()

    captured = capsys.readouterr()
    assert "Test" in captured.out
