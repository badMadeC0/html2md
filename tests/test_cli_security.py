"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import socket

import pytest

from html2md import cli


def _addrinfo_for(*ips):
    """Build getaddrinfo-style results for resolved IPv4/IPv6 addresses."""
    results = []
    for ip in ips:
        family = socket.AF_INET6 if ":" in ip else socket.AF_INET
        sockaddr = (ip, 0, 0, 0) if family == socket.AF_INET6 else (ip, 0)
        results.append((family, socket.SOCK_STREAM, 6, "", sockaddr))
    return results


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
    "url, resolved_ip",
    [
        ("http://127.0.0.1:8080/admin", "127.0.0.1"),
        ("http://localhost/secret", "127.0.0.1"),
        ("http://192.168.1.1/config", "192.168.1.1"),
        ("http://10.0.0.5/", "10.0.0.5"),
        ("http://100.64.0.1/", "100.64.0.1"),
        ("http://multicast.test/", "224.0.0.1"),
        ("http://ipv6-multicast.test/", "ff02::1"),
        ("http://nat64-reserved.test/", "64:ff9b::7f00:1"),
        ("http://mapped-cgnat.test/", "::ffff:100.64.0.1"),
        ("http://mapped-multicast.test/", "::ffff:224.0.0.1"),
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, resolved_ip):
    """Ensure that restricted IPs are blocked to prevent SSRF."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for(resolved_ip),
    ):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_rejects_mixed_dns_results(mock_get, capsys, tmp_path):
    """Reject a hostname if any resolved address is restricted."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for("93.184.216.34", "10.0.0.5"),
    ):
        cli.main(["--url", "http://example.com/", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_accepts_all_global_dns_results(mock_get, capsys, tmp_path):
    """Accept a hostname only when every resolved address is globally routable."""
    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for(
            "93.184.216.34",
            "2606:2800:220:1:248:1893:25c8:1946",
        ),
    ):
        cli.main(["--url", "http://example.com/", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    mock_get.assert_called_once()


@patch("requests.Session.get")
def test_process_url_allows_ipv4_mapped_ipv6_for_global_address(mock_get, capsys, tmp_path):
    """IPv4-mapped IPv6 addresses are allowed only when the mapped IPv4 is global."""
    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=_addrinfo_for("::ffff:93.184.216.34"),
    ):
        cli.main(["--url", "http://example.com/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert "restricted/private" not in outerr.err
    mock_get.assert_called_once()


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
            return_value=_addrinfo_for("93.184.216.34"),
        ):
            cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
