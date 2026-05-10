"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import pytest

from html2md import cli


def addrinfo(*ip_addresses):
    """Build deterministic getaddrinfo-style results for tests."""
    return [
        (None, None, None, None, (ip_address, 0))
        for ip_address in ip_addresses
    ]


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
        ("http://localhost/secret", "::1"),
        ("http://192.168.1.1/config", "192.168.1.1"),
        ("http://10.0.0.5/", "10.0.0.5"),
        ("http://100.64.0.1/", "100.64.0.1"),
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, resolved_ip):
    """Ensure that non-global addresses are blocked to prevent SSRF."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=addrinfo(resolved_ip),
    ):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert (
        "Error: URL resolves to a restricted/private network address."
        in outerr.err
    )
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_allows_global_ipv6_address(mock_get, capsys, tmp_path):
    """Public IPv6 addresses are valid URL targets."""
    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=addrinfo("2606:4700:4700::1111"),
    ):
        cli.main([
            "--url",
            "https://[2606:4700:4700::1111]/",
            "--outdir",
            str(tmp_path),
        ])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert "restricted/private" not in outerr.err
    mock_get.assert_called_once()


@patch("requests.Session.get")
def test_process_url_blocks_any_non_global_address(mock_get, capsys, tmp_path):
    """Every address from getaddrinfo must be globally reachable."""
    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=addrinfo("93.184.216.34", "fd00::1"),
    ):
        cli.main(["--url", "https://example.com", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert (
        "Error: URL resolves to a restricted/private network address."
        in outerr.err
    )
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

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=addrinfo("93.184.216.34"),
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
