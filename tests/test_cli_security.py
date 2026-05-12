"""Security-focused tests for CLI URL and output path handling."""

import socket
from unittest.mock import MagicMock, patch
import pytest

from html2md import cli


def _addrinfo(ip, port=80, family=None):
    """Build a getaddrinfo-style stream tuple for IPv4 or IPv6 tests."""
    ip_family = family or (socket.AF_INET6 if ":" in ip else socket.AF_INET)
    sockaddr = (ip, port, 0, 0) if ip_family == socket.AF_INET6 else (ip, port)
    return (ip_family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", sockaddr)


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
        ("http://[::1]/", "::1"),
        ("http://100.64.0.1/", "100.64.0.1"),
        ("http://0.0.0.0/", "0.0.0.0"),
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url, resolved_ip):
    """Ensure that non-global, private, and loopback IPs are blocked to prevent SSRF."""
    with patch("html2md.cli.socket.getaddrinfo", return_value=[_addrinfo(resolved_ip)]):
        cli.main(["--url", url, "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_process_url_allows_public_ipv6(mock_get, capsys, tmp_path):
    """Public IPv6 literal URLs remain fetchable after SSRF validation."""
    response = MagicMock()
    response.text = "<h1>IPv6</h1>"
    response.is_redirect = False
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    with patch(
        "html2md.cli.socket.getaddrinfo",
        return_value=[_addrinfo("2606:4700:4700::1111", port=443)],
    ):
        cli.main(["--url", "https://[2606:4700:4700::1111]/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert "restricted/private" not in outerr.err
    mock_get.assert_called_once_with(
        "https://[2606:4700:4700::1111]/", timeout=30, allow_redirects=False
    )


@patch("requests.Session.get")
def test_process_url_does_not_swap_global_resolver(mock_get, capsys, tmp_path):
    """Fetching with pinned DNS must not monkey-patch socket.getaddrinfo globally."""
    public_addrinfo = _addrinfo("93.184.216.34")
    rebound_addrinfo = _addrinfo("127.0.0.1")
    real_getaddrinfo = cli.socket.getaddrinfo
    lookup_count = 0

    def rebinding_getaddrinfo(host, port, *args, **kwargs):
        nonlocal lookup_count
        if host == "rebind.example":
            lookup_count += 1
            return [public_addrinfo] if lookup_count == 1 else [rebound_addrinfo]
        return real_getaddrinfo(host, port, *args, **kwargs)

    def request_side_effect(url, timeout, allow_redirects):
        assert url == "http://rebind.example/"
        assert timeout == 30
        assert allow_redirects is False
        # The global resolver remains untouched; pinning is scoped to the adapter.
        assert cli.socket.getaddrinfo("rebind.example", 80) == [rebound_addrinfo]
        response = MagicMock()
        response.text = "<h1>safe</h1>"
        response.is_redirect = False
        response.raise_for_status.return_value = None
        return response

    mock_get.side_effect = request_side_effect

    with patch("html2md.cli.socket.getaddrinfo", side_effect=rebinding_getaddrinfo):
        cli.main(["--url", "http://rebind.example/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out


def test_pinned_adapter_connects_to_vetted_address_without_dns_lookup():
    """The adapter opens sockets to vetted addresses without resolving the host again."""
    public_addrinfo = _addrinfo("93.184.216.34")
    created_sockets = []

    class FakeSocket:
        def __init__(self, family, socktype, proto):
            self.family = family
            self.socktype = socktype
            self.proto = proto
            self.connected_to = None
            self.closed = False

        def setsockopt(self, *args):
            pass

        def settimeout(self, timeout):
            self.timeout = timeout

        def bind(self, source_address):
            self.source_address = source_address

        def connect(self, sockaddr):
            self.connected_to = sockaddr

        def close(self):
            self.closed = True

    def fake_socket(family, socktype, proto):
        sock = FakeSocket(family, socktype, proto)
        created_sockets.append(sock)
        return sock

    adapter = cli._build_pinned_dns_adapter([public_addrinfo])
    pool = adapter.poolmanager.connection_from_url("http://rebind.example/")
    connection = pool._new_conn()

    with patch(
        "html2md.cli.socket.getaddrinfo",
        side_effect=AssertionError("unexpected DNS lookup"),
    ):
        with patch("html2md.cli.socket.socket", side_effect=fake_socket):
            sock = connection._new_conn()

    assert sock is created_sockets[0]
    assert sock.connected_to == public_addrinfo[4]


@patch("requests.Session.get")
def test_process_url_pins_idna_normalized_hostname(mock_get, capsys, tmp_path):
    """DNS pinning matches the IDNA hostname urllib3 resolves for Unicode domains."""
    public_addrinfo = _addrinfo("93.184.216.34")
    rebound_addrinfo = _addrinfo("127.0.0.1")
    real_getaddrinfo = cli.socket.getaddrinfo
    lookup_count = 0

    def rebinding_getaddrinfo(host, port, *args, **kwargs):
        nonlocal lookup_count
        if host in {"éxample.com", "xn--xample-9ua.com"}:
            lookup_count += 1
            return [public_addrinfo] if lookup_count == 1 else [rebound_addrinfo]
        return real_getaddrinfo(host, port, *args, **kwargs)

    def request_side_effect(url, timeout, allow_redirects):
        assert url == "http://éxample.com/"
        assert timeout == 30
        assert allow_redirects is False
        # The global resolver is not monkey-patched; in this deterministic
        # rebinding stub, the second lookup returns the rebound address.
        assert cli.socket.getaddrinfo("xn--xample-9ua.com", 80) == [rebound_addrinfo]
        response = MagicMock()
        response.text = "<h1>safe</h1>"
        response.is_redirect = False
        response.raise_for_status.return_value = None
        return response

    mock_get.side_effect = request_side_effect

    with patch("html2md.cli.socket.getaddrinfo", side_effect=rebinding_getaddrinfo):
        cli.main(["--url", "http://éxample.com/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out


@patch("requests.Session.get")
def test_process_url_validates_redirect_targets(mock_get, capsys, tmp_path):
    """Redirect locations are revalidated before following them."""
    redirect_response = MagicMock()
    redirect_response.is_redirect = True
    redirect_response.headers = {"Location": "http://127.0.0.1/admin"}
    mock_get.return_value = redirect_response

    def resolver(host, port, *args, **kwargs):
        if host == "public.example":
            return [_addrinfo("93.184.216.34", port=port)]
        if host == "127.0.0.1":
            return [_addrinfo("127.0.0.1", port=port)]
        raise socket.gaierror(host)

    with patch("html2md.cli.socket.getaddrinfo", side_effect=resolver):
        cli.main(["--url", "http://public.example/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: URL resolves to a restricted/private network address." in outerr.err
    mock_get.assert_called_once_with("http://public.example/", timeout=30, allow_redirects=False)


@patch("requests.Session.get")
def test_redirect_response_is_closed_before_next_hop(mock_get):
    """Redirect responses that are not returned are closed before following."""
    redirect_response = MagicMock()
    redirect_response.is_redirect = True
    redirect_response.headers = {"Location": "http://next.example/"}

    final_response = MagicMock()
    final_response.is_redirect = False
    final_response.headers = {}
    mock_get.side_effect = [redirect_response, final_response]

    def resolver(host, port, *args, **kwargs):
        if host in {"public.example", "next.example"}:
            return [_addrinfo("93.184.216.34", port=port)]
        raise socket.gaierror(host)

    with patch("html2md.cli.socket.getaddrinfo", side_effect=resolver):
        assert cli._safe_get(MagicMock(), "http://public.example/") is final_response

    redirect_response.close.assert_called_once_with()


@patch("requests.Session.get", autospec=True)
def test_redirect_set_cookie_is_preserved_for_next_hop(mock_get):
    """Cookies learned from redirect responses are available to later hops."""
    import requests

    redirect_response = MagicMock()
    redirect_response.is_redirect = True
    redirect_response.headers = {"Location": "http://next.example/"}

    final_response = MagicMock()
    final_response.is_redirect = False
    final_response.headers = {}

    def request_side_effect(pinned_session, url, timeout, allow_redirects):
        assert timeout == 30
        assert allow_redirects is False
        if url == "http://public.example/":
            assert pinned_session.cookies.get("redirect_token") is None
            pinned_session.cookies.set("redirect_token", "secret")
            return redirect_response
        if url == "http://next.example/":
            assert pinned_session.cookies.get("redirect_token") == "secret"
            return final_response
        raise AssertionError(f"unexpected URL: {url}")

    mock_get.side_effect = request_side_effect

    def resolver(host, port, *args, **kwargs):
        if host in {"public.example", "next.example"}:
            return [_addrinfo("93.184.216.34", port=port)]
        raise socket.gaierror(host)

    session = requests.Session()
    with patch("html2md.cli.socket.getaddrinfo", side_effect=resolver):
        assert cli._safe_get(session, "http://public.example/") is final_response

    assert session.cookies.get("redirect_token") == "secret"


@patch("requests.Session.get")
def test_empty_dns_answer_reports_resolution_error(mock_get, capsys, tmp_path):
    """An empty DNS response is reported as a resolution failure, not SSRF."""
    with patch("html2md.cli.socket.getaddrinfo", return_value=[]):
        cli.main(["--url", "http://empty.example/", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Error: Could not resolve hostname to a valid IP." in outerr.err
    assert "restricted/private" not in outerr.err
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
    response.is_redirect = False
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    urls = [
        "http://example.com/foo/../..%2Fsecret.txt",
        "http://example.com/foo/%2E%2E%2F%2E%2E%2Fsecret.txt",
    ]

    with patch("html2md.cli.socket.getaddrinfo", return_value=[_addrinfo("93.184.216.34")]):
        for url in urls:
            cli.main(["--url", url, "--outdir", str(outdir)])
            outerr = capsys.readouterr()
            assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
