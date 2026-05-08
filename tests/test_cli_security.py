"""Security-focused tests for CLI URL and output path handling."""

import socket
from unittest.mock import MagicMock, patch

import pytest
import urllib3.connection

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


@patch("html2md.cli.socket.getaddrinfo")
@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """Traversal-like URL paths must never write outside of --outdir."""
    mock_getaddrinfo.return_value = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))
    ]

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
        cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(
        outdir.rglob("*.md")
    ), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()


@pytest.mark.parametrize(
    "url",
    [
        "http://127.0.0.1/",
        "http://localhost/",
        "http://169.254.169.254/latest/meta-data/",
        "http://10.0.0.1/",
        "http://192.168.1.1/",
        "http://172.16.0.1/",
        "http://0.0.0.0/",
        "http://100.64.0.1/",
        "http://198.18.0.1/",
        "http://[::1]/",
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection_blocked(mock_get, capsys, tmp_path, url):
    """SSRF protection should block internal/private/loopback/metadata IP addresses."""
    cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert f"Error: URL '{url}' resolves to a non-public IP address." in outerr.err
    mock_get.assert_not_called()


@pytest.mark.parametrize(
    "nat64_address, embedded_ipv4",
    [
        ("64:ff9b::a9fe:a9fe", "169.254.169.254"),
        ("64:ff9b::a00:1", "10.0.0.1"),
        ("64:ff9b::7f00:1", "127.0.0.1"),
    ],
)
@patch("html2md.cli.socket.getaddrinfo")
def test_global_addr_info_blocks_nat64_embedded_non_public_ipv4(
    mock_getaddrinfo, nat64_address, embedded_ipv4
):
    """NAT64 answers must not tunnel SSRF fetches to embedded private targets."""
    mock_getaddrinfo.return_value = [
        (socket.AF_INET6, socket.SOCK_STREAM, 6, "", (nat64_address, 443, 0, 0))
    ]

    with pytest.raises(cli.UnsafeUrlError) as excinfo:
        cli._global_addr_info("example.com", 443)  # pylint: disable=protected-access

    assert nat64_address in str(excinfo.value)
    assert embedded_ipv4 in str(excinfo.value)


@patch("html2md.cli.socket.getaddrinfo")
def test_global_addr_info_allows_nat64_embedded_public_ipv4(mock_getaddrinfo):
    """NAT64 answers remain allowed when their embedded IPv4 target is public."""
    mock_getaddrinfo.return_value = [
        (socket.AF_INET6, socket.SOCK_STREAM, 6, "", ("64:ff9b::808:808", 443, 0, 0))
    ]

    assert cli._global_addr_info("example.com", 443) == mock_getaddrinfo.return_value


@patch("html2md.cli.socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_ssrf_protection_allowed(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """SSRF protection should allow public IP addresses."""
    # Mock getaddrinfo to return a public IP
    mock_getaddrinfo.return_value = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))  # example.com
    ]

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    mock_get.assert_called_once()


@patch("html2md.cli.socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_revalidates_redirect_target(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """Redirect targets must pass SSRF validation before being fetched."""

    def fake_getaddrinfo(hostname, port, *args, **kwargs):
        del port, args, kwargs
        if hostname == "example.com":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))]
        if hostname == "169.254.169.254":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 0))]
        raise socket.gaierror(hostname)

    redirect = MagicMock()
    redirect.status_code = 302
    redirect.headers = {"Location": "http://169.254.169.254/latest/meta-data/"}
    mock_get.return_value = redirect
    mock_getaddrinfo.side_effect = fake_getaddrinfo

    cli.main(["--url", "http://example.com/", "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()

    assert "http://169.254.169.254/latest/meta-data/" in outerr.err
    assert "resolves to a non-public IP address" in outerr.err
    mock_get.assert_called_once_with(
        "http://example.com/", timeout=30, allow_redirects=False
    )


def test_safe_session_get_disables_environment_proxies(monkeypatch):
    """SSRF-protected fetches must not honor HTTP(S)_PROXY from the environment."""
    monkeypatch.setenv("HTTP_PROXY", "http://proxy.example:8080")
    monkeypatch.setenv("HTTPS_PROXY", "http://proxy.example:8080")

    session = MagicMock()
    session.trust_env = True
    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    session.get.return_value = response

    with patch("html2md.cli.is_safe_url", return_value=True), patch(
        "html2md.cli._ssrf_safe_connection"
    ) as mock_safe_connection:
        mock_safe_connection.return_value.__enter__.return_value = None
        mock_safe_connection.return_value.__exit__.return_value = None

        assert cli._safe_session_get(session, "https://example.com/") is response

    assert session.trust_env is False
    session.get.assert_called_once_with(
        "https://example.com/", timeout=30, allow_redirects=False
    )


@patch("html2md.cli.socket.getaddrinfo")
def test_safe_connection_validates_and_pins_actual_connect_address(mock_getaddrinfo):
    """The socket connect helper rejects a rebinding answer before connecting."""
    mock_getaddrinfo.return_value = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 80))
    ]

    with cli._ssrf_safe_connection():  # pylint: disable=protected-access
        with pytest.raises(cli.UnsafeUrlError):
            urllib3.connection.connection.create_connection(("example.com", 80))
