"""Security-focused tests for CLI URL and output path handling."""

import sys
import types
from unittest.mock import MagicMock, patch

import pytest

from html2md import cli


def addrinfo(ip, port=80):
    """Build a socket.getaddrinfo-style result for tests."""
    family = cli.socket.AF_INET6 if ":" in ip else cli.socket.AF_INET
    sockaddr = (ip, port, 0, 0) if family == cli.socket.AF_INET6 else (ip, port)
    return [(family, cli.socket.SOCK_STREAM, 6, "", sockaddr)]


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
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, resolved_ip):
    """Ensure that non-global IPs are blocked to prevent SSRF."""
    with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo(resolved_ip)):
        cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_allows_public_ipv6(mock_get, capsys, tmp_path):
    """Public IPv6 targets remain supported by the SSRF guard."""
    response = MagicMock()
    response.status_code = 200
    response.text = "<h1>ipv6</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo("2606:4700:4700::1111")):
        cli.main(["--url", "https://[2606:4700:4700::1111]/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert outerr.err == ""
    mock_get.assert_called_once_with(
        "https://[2606:4700:4700::1111]/", timeout=30, allow_redirects=False
    )


@patch("requests.Session.get")
def test_process_url_blocks_redirect_to_private_address(mock_get, capsys, tmp_path):
    """Redirect targets are validated before the CLI follows them."""
    redirect_response = MagicMock()
    redirect_response.status_code = 302
    redirect_response.headers = {"Location": "http://127.0.0.1:8080/admin"}
    mock_get.return_value = redirect_response

    def resolve_by_host(hostname, port, *args, **kwargs):
        if hostname == "public.example":
            return addrinfo("93.184.216.34", port)
        if hostname == "127.0.0.1":
            return addrinfo("127.0.0.1", port)
        raise AssertionError(f"Unexpected hostname: {hostname}")

    with patch("html2md.cli.socket.getaddrinfo", side_effect=resolve_by_host):
        cli.main(["--url", "http://public.example/start", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_called_once_with(
        "http://public.example/start", timeout=30, allow_redirects=False
    )


def test_process_url_uses_requests_connection_module_for_rebinding_guard(capsys):
    """The CLI patches the create_connection symbol requests/urllib3 calls."""
    fake_requests = types.ModuleType("requests")
    fake_requests.RequestException = RuntimeError
    fake_requests.Session = MagicMock(return_value=MagicMock())
    fake_markdownify = types.ModuleType("markdownify")
    fake_markdownify.markdownify = MagicMock(return_value="guarded")
    fake_urllib3 = types.ModuleType("urllib3")
    fake_connection = types.ModuleType("urllib3.connection")
    fake_connection.create_connection = MagicMock()
    fake_urllib3.connection = fake_connection

    response = MagicMock()
    response.text = "<h1>guarded</h1>"
    response.raise_for_status.return_value = None
    captured = {}

    def fake_fetch(session, target_url, connection_module, timeout=30):
        captured["connection_module"] = connection_module
        return response

    modules = {
        "requests": fake_requests,
        "markdownify": fake_markdownify,
        "urllib3": fake_urllib3,
        "urllib3.connection": fake_connection,
    }
    with patch.dict(sys.modules, modules):
        with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo("93.184.216.34")):
            with patch("html2md.cli._fetch_with_validated_redirects", side_effect=fake_fetch):
                cli.main(["--url", "http://public.example/start"])

    outerr = capsys.readouterr()
    assert "guarded" in outerr.out
    assert outerr.err == ""
    assert captured["connection_module"] is fake_connection


def test_validated_fetch_disables_environment_proxy_settings():
    """Validated fetches must not use HTTP_PROXY/HTTPS_PROXY from the environment."""
    session = MagicMock()
    session.trust_env = True
    response = MagicMock()
    response.status_code = 200
    session.get.return_value = response
    connection_module = MagicMock()

    with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo("93.184.216.34")):
        result = cli._fetch_with_validated_redirects(
            session, "http://public.example/start", connection_module
        )

    assert result is response
    assert session.trust_env is False
    session.get.assert_called_once_with(
        "http://public.example/start", timeout=30, allow_redirects=False
    )


def test_validated_fetch_returns_open_redirect_response_without_location():
    """Redirect responses without Location are returned open for caller handling."""
    session = MagicMock()
    response = MagicMock()
    response.status_code = 302
    response.headers = {}
    session.get.return_value = response
    connection_module = MagicMock()

    with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo("93.184.216.34")):
        result = cli._fetch_with_validated_redirects(
            session, "http://public.example/start", connection_module
        )

    assert result is response
    response.close.assert_not_called()


def test_validated_create_connection_rejects_mixed_private_candidates():
    """The connection resolver refuses hostnames with any restricted candidate."""
    mixed_addresses = addrinfo("93.184.216.34") + addrinfo("127.0.0.1")
    with patch("html2md.cli.socket.getaddrinfo", return_value=mixed_addresses):
        with patch("html2md.cli.socket.socket") as mock_socket:
            with pytest.raises(PermissionError):
                cli._validated_create_connection(("mixed.example", 80))

    mock_socket.assert_not_called()


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
        with patch("html2md.cli.socket.getaddrinfo", return_value=addrinfo("93.184.216.34")):
            cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
