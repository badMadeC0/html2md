"""Security-focused tests for CLI URL and output path handling."""

import socket
from unittest.mock import MagicMock, patch
import pytest

from html2md import cli


def _addrinfo_for(ip):
    """Build a getaddrinfo-style result for a deterministic IP address."""
    family = socket.AF_INET6 if ":" in ip else socket.AF_INET
    return [(family, socket.SOCK_STREAM, 0, "", (ip, 443))]


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
    "url, ip",
    [
        ("http://127.0.0.1:8080/admin", "127.0.0.1"),
        ("http://localhost/secret", "127.0.0.1"),
        ("http://192.168.1.1/config", "192.168.1.1"),
        ("http://10.0.0.5/", "10.0.0.5"),
        ("http://[::1]/", "::1"),
        ("http://100.64.0.1/", "100.64.0.1"),
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, ip):
    """Ensure that non-global IPs are blocked to prevent SSRF."""
    with patch("html2md.cli.socket.getaddrinfo", return_value=_addrinfo_for(ip)):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_allows_public_ipv6(mock_get, capsys, tmp_path):
    """Public IPv6 targets should remain valid after SSRF validation."""
    response = MagicMock()
    response.status_code = 200
    response.text = "<h1>ipv6</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for("2606:4700:4700::1111"),
    ):
        cli.main([
            "--url",
            "https://[2606:4700:4700::1111]/",
            "--outdir",
            str(tmp_path),
        ])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    mock_get.assert_called_once_with(
        "https://[2606:4700:4700::1111]/", timeout=30, allow_redirects=False
    )


@patch("requests.Session.get")
def test_process_url_blocks_redirect_to_private_address(mock_get, capsys, tmp_path):
    """Redirect targets are validated before the redirected request is fetched."""
    redirect = MagicMock()
    redirect.status_code = 302
    redirect.headers = {"Location": "http://127.0.0.1:8080/admin"}
    mock_get.return_value = redirect

    def resolve(hostname, port, type):  # pylint: disable=redefined-builtin
        if hostname == "example.com":
            return _addrinfo_for("93.184.216.34")
        if hostname == "127.0.0.1":
            return _addrinfo_for("127.0.0.1")
        raise AssertionError(f"Unexpected hostname: {hostname}")

    with patch("html2md.cli.socket.getaddrinfo", side_effect=resolve):
        cli.main(["--url", "https://example.com/start", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_called_once_with(
        "https://example.com/start", timeout=30, allow_redirects=False
    )


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

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for("93.184.216.34"),
    ):
        for url in urls:
            cli.main(["--url", url, "--outdir", str(outdir)])
            outerr = capsys.readouterr()
            assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), (
        "No markdown files were created in the output directory."
    )
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
