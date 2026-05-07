"""Security-focused tests for CLI URL and output path handling."""

import socket
from unittest.mock import MagicMock, patch
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
    "url,internal_ip",
    [
        ("http://localhost:8080/admin", "127.0.0.1"),
        ("http://127.0.0.1/status", "127.0.0.1"),
        ("http://169.254.169.254/latest/meta-data/", "169.254.169.254"),
        ("https://192.168.1.1/config", "192.168.1.1"),
        ("http://[::1]/", "::1"),
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, internal_ip):
    """Ensure URLs pointing to private/internal IPs are rejected to prevent SSRF."""
    with patch("socket.getaddrinfo", return_value=[(2, 1, 6, "", (internal_ip, 0))]):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Unsafe URL pointing to internal IP" in outerr.err
    mock_get.assert_not_called()


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(mock_get, mock_getaddrinfo, capsys, tmp_path):
    """Traversal-like URL paths must never write outside of --outdir."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret content", encoding="utf-8")

    mock_getaddrinfo.return_value = [(2, 1, 6, "", ("93.184.216.34", 80))]

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    urls = [
        "http://example.com/foo/../..%2Fsecret.txt",
        "http://example.com/foo/%2E%2E%2F%2E%2E%2Fsecret.txt",
    ]

    for url in urls:
        cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_blocks_redirects(mock_get, mock_getaddrinfo, capsys, tmp_path):
    """Redirect responses are rejected instead of following to unvalidated hosts."""
    mock_getaddrinfo.return_value = [
        (2, 1, 6, "", ("93.184.216.34", 443)),
    ]
    response = MagicMock()
    response.status_code = 302
    mock_get.return_value = response

    cli.main(["--url", "https://example.com/redirect", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Redirects are not allowed" in outerr.err
    mock_get.assert_called_once_with(
        "https://example.com/redirect", timeout=30, allow_redirects=False
    )


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_revalidates_dns_during_fetch(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """DNS answers used by the actual fetch are revalidated to reduce rebinding risk."""
    public_answer = [(2, 1, 6, "", ("93.184.216.34", 443))]
    private_answer = [(2, 1, 6, "", ("127.0.0.1", 443))]
    mock_getaddrinfo.side_effect = [public_answer, private_answer]

    def fetch_with_rebound_dns(*_args, **_kwargs):
        socket.getaddrinfo("example.com", 443)

    mock_get.side_effect = fetch_with_rebound_dns

    cli.main(["--url", "https://example.com", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Unsafe URL pointing to internal IP '127.0.0.1'" in outerr.err
