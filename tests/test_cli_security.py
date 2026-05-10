"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import socket
import pytest

from html2md import cli


@pytest.mark.parametrize(
    "url, scheme",
    [
        ("file:///etc/passwd", "file"),
        ("ftp://example.com/data.txt", "ftp"),
        ("example.com/data.txt", ""),
    ],
)
@patch("requests.Session.get")
def test_process_url_unsupported_scheme(mock_get, capsys, tmp_path, url, scheme):
    """Unsupported schemes are rejected before any network call."""
    cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert f"Error: Unsupported URL scheme '{scheme}'." in outerr.err
    mock_get.assert_not_called()


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1:8080/admin",
        "http://localhost/secret",
        "http://192.168.1.1/config",
        "http://10.0.0.5/",
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url):
    """Ensure that local, private, and loopback IPs are blocked to prevent SSRF."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))],
    ):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(mock_get, capsys, tmp_path):
    """Traversal-like URL paths must never write outside of --outdir."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret content", encoding="utf-8")

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    urls = [
        "http://example.com/foo/../..%2Fsecret.txt",
        "http://example.com/foo/%2E%2E%2F%2E%2E%2Fsecret.txt",
    ]

    for url in urls:
        with patch(
            "html2md.cli.socket.getaddrinfo",
            return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))],
        ):
            cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()


@patch("requests.Session.get")
def test_process_url_allows_public_ipv6(mock_get, capsys, tmp_path):
    """Public IPv6 targets remain allowed."""
    response = MagicMock()
    response.text = "<h1>ok</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=[(socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("2001:4860:4860::8888", 443, 0, 0))],
    ):
        cli.main(["--url", "https://ipv6.example.test", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert "Error:" not in outerr.err
    mock_get.assert_called_once()


@patch("requests.Session.get")
def test_process_url_blocks_when_any_resolved_ip_is_private(mock_get, capsys, tmp_path):
    """A hostname is blocked if any resolved address is restricted."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=[
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80)),
        ],
    ):
        cli.main(["--url", "http://example.com", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_blocks_redirect_responses(mock_get, capsys, tmp_path):
    """Redirect responses are rejected to prevent redirect SSRF bypasses."""
    response = MagicMock()
    response.status_code = 302
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=[(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))],
    ):
        cli.main(["--url", "http://example.com", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: Redirect responses are not allowed." in outerr.err
    mock_get.assert_called_once()
    assert mock_get.call_args.kwargs.get("allow_redirects") is False
