"""Security-focused tests for CLI URL and output path handling."""
from __future__ import annotations

import ipaddress
import socket
from unittest.mock import MagicMock, patch

import pytest

from html2md import cli
from html2md.cli import _check_ssrf


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _make_addrinfo(ip: str):
    """Build a minimal ``getaddrinfo`` result list for *ip*."""
    if ':' in ip:
        family = socket.AF_INET6
        sockaddr = (ip, 0, 0, 0)
    else:
        family = socket.AF_INET
        sockaddr = (ip, 0)
    return [(family, socket.SOCK_STREAM, 6, '', sockaddr)]


# Public IP used by example.com – globally routable so _check_ssrf allows it.
_EXAMPLE_COM_ADDRINFO = _make_addrinfo("93.184.216.34")


# ---------------------------------------------------------------------------
# _check_ssrf unit tests (no real DNS lookups)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("blocked_ip", [
    "127.0.0.1",        # loopback
    "::1",              # IPv6 loopback
    "169.254.169.254",  # link-local / AWS metadata
    "10.0.0.1",         # private class A
    "192.168.1.1",      # private class C
    "172.16.0.1",       # private class B
    "224.0.0.1",        # multicast
])
def test_check_ssrf_blocks_non_public(blocked_ip):
    """_check_ssrf must raise ValueError for any non-globally-routable address."""
    with patch("socket.getaddrinfo", return_value=_make_addrinfo(blocked_ip)):
        with pytest.raises(ValueError, match="SSRF blocked"):
            _check_ssrf("internal.example")


def test_check_ssrf_raises_on_unresolvable():
    """_check_ssrf must raise ValueError when the hostname cannot be resolved."""
    with patch("socket.getaddrinfo", side_effect=OSError("Name or service not known")):
        with pytest.raises(ValueError, match="Could not resolve"):
            _check_ssrf("nonexistent.invalid")


def test_check_ssrf_allows_public_ip():
    """_check_ssrf must not raise for a globally-routable public address."""
    public_ip = "93.184.216.34"  # example.com
    assert ipaddress.ip_address(public_ip).is_global
    with patch("socket.getaddrinfo", return_value=_make_addrinfo(public_ip)):
        _check_ssrf("example.com")  # should not raise


def test_check_ssrf_validates_all_addresses():
    """_check_ssrf must raise if *any* resolved address is non-public (multi-address hosts)."""
    public_ip = "93.184.216.34"
    private_ip = "10.0.0.1"
    addrinfo = _make_addrinfo(public_ip) + _make_addrinfo(private_ip)
    with patch("socket.getaddrinfo", return_value=addrinfo):
        with pytest.raises(ValueError, match="SSRF blocked"):
            _check_ssrf("dual.example")


def test_check_ssrf_strips_ipv6_scope_id():
    """_check_ssrf must correctly strip the IPv6 scope-id before parsing."""
    # fe80::1%eth0 is link-local; after scope stripping it must still be blocked.
    scoped = "fe80::1%eth0"
    sockaddr = (scoped, 0, 0, 0)
    addrinfo = [(socket.AF_INET6, socket.SOCK_STREAM, 6, '', sockaddr)]
    with patch("socket.getaddrinfo", return_value=addrinfo):
        with pytest.raises(ValueError, match="SSRF blocked"):
            _check_ssrf("link-local.example")


# ---------------------------------------------------------------------------
# Integration tests: CLI rejects SSRF targets via process_url
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("ssrf_url,blocked_ip", [
    ("http://localhost/", "127.0.0.1"),
    ("http://169.254.169.254/latest/meta-data/", "169.254.169.254"),
    ("http://internal.corp/secret", "10.0.0.1"),
])
def test_process_url_blocks_ssrf(ssrf_url, blocked_ip, capsys):
    """CLI must reject URLs that resolve to non-public IPs."""
    with patch("socket.getaddrinfo", return_value=_make_addrinfo(blocked_ip)):
        with patch("requests.Session.get") as mock_get:
            cli.main(["--url", ssrf_url])
            mock_get.assert_not_called()
    outerr = capsys.readouterr()
    assert "SSRF blocked" in outerr.err


# ---------------------------------------------------------------------------
# Existing scheme / path-traversal tests (preserved, now with SSRF mock)
# ---------------------------------------------------------------------------

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


@patch("socket.getaddrinfo", return_value=_EXAMPLE_COM_ADDRINFO)
@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(mock_get, mock_addrinfo, capsys, tmp_path):
    """Traversal-like URL paths must never write outside of --outdir."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret content", encoding="utf-8")

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    response.status_code = 200
    response.headers = {}
    response.iter_content.return_value = iter([b"<h1>dummy</h1>"])
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

