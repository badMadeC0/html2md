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
        "http://localhost:8080/admin",
        "http://127.0.0.1/status",
        "http://169.254.169.254/latest/meta-data/",
        "https://192.168.1.1/config",
        "http://[::1]/",
    ],
)
@patch("requests.Session.get")
def test_process_url_ssrf_protection(mock_get, capsys, tmp_path, url):
    """Ensure URLs pointing to private/internal IPs are rejected to prevent SSRF."""
    cli.main(["--url", url, "--outdir", str(tmp_path)])
    outerr = capsys.readouterr()
    assert "Unsafe URL pointing to internal IP" in outerr.err or "Error validating hostname" in outerr.err
    mock_get.assert_not_called()


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_redirect_to_internal_ip_is_blocked(mock_get, mock_getaddrinfo, capsys):
    """Redirect targets are validated before a follow-up request is sent."""
    mock_getaddrinfo.side_effect = [
        [(None, None, None, None, ("8.8.8.8", 0))],
        [(None, None, None, None, ("169.254.169.254", 0))],
    ]

    redirect_response = MagicMock()
    redirect_response.status_code = 302
    redirect_response.headers = {"Location": "http://169.254.169.254/latest/meta-data/"}
    mock_get.return_value = redirect_response

    cli.main(["--url", "http://public.example/redirect"])

    outerr = capsys.readouterr()
    assert "Unsafe URL pointing to internal IP '169.254.169.254'" in outerr.err
    mock_get.assert_called_once_with(
        "http://public.example/redirect", timeout=30, allow_redirects=False
    )


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_safe_redirect_is_manually_followed(mock_get, mock_getaddrinfo, capsys):
    """Safe redirect targets are validated and then fetched without auto-redirects."""
    mock_getaddrinfo.return_value = [(None, None, None, None, ("8.8.8.8", 0))]

    redirect_response = MagicMock()
    redirect_response.status_code = 302
    redirect_response.headers = {"Location": "/final"}

    final_response = MagicMock()
    final_response.status_code = 200
    final_response.headers = {}
    final_response.text = "<h1>Safe</h1>"
    final_response.raise_for_status.return_value = None

    mock_get.side_effect = [redirect_response, final_response]

    cli.main(["--url", "http://public.example/start"])

    outerr = capsys.readouterr()
    assert "# Safe" in outerr.out
    assert mock_get.call_args_list[0].args == ("http://public.example/start",)
    assert mock_get.call_args_list[0].kwargs["allow_redirects"] is False
    assert mock_get.call_args_list[1].args == ("http://public.example/final",)
    assert mock_get.call_args_list[1].kwargs["allow_redirects"] is False


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_validated_dns_answer_is_pinned_during_fetch(mock_get, mock_getaddrinfo, capsys):
    """The request uses the DNS answer validated before fetching."""
    public_answer = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 80))]
    rebound_answer = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 80))]
    mock_getaddrinfo.side_effect = [public_answer, rebound_answer]

    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.text = "<h1>Pinned</h1>"
    response.raise_for_status.return_value = None

    def get_with_pinned_dns(*_args, **_kwargs):
        resolved = socket.getaddrinfo("rebinding.example", 80, type=socket.SOCK_STREAM)
        assert resolved == public_answer
        return response

    mock_get.side_effect = get_with_pinned_dns

    cli.main(["--url", "http://rebinding.example/"])

    outerr = capsys.readouterr()
    assert "# Pinned" in outerr.out
    assert "169.254.169.254" not in outerr.err
    assert mock_getaddrinfo.call_count == 1
    mock_get.assert_called_once_with(
        "http://rebinding.example/", timeout=30, allow_redirects=False
    )


@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_idna_hostname_uses_pinned_validated_dns(mock_get, mock_getaddrinfo, capsys):
    """Unicode hostnames are normalized before validation and pinned lookup matching."""
    public_answer = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 80))]
    rebound_answer = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("169.254.169.254", 80))]
    mock_getaddrinfo.side_effect = [public_answer, rebound_answer]

    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.text = "<h1>IDNA pinned</h1>"
    response.raise_for_status.return_value = None

    def get_with_idna_hostname(*_args, **_kwargs):
        resolved = socket.getaddrinfo("xn--tst-qla.example", 80, type=socket.SOCK_STREAM)
        assert resolved == public_answer
        return response

    mock_get.side_effect = get_with_idna_hostname

    cli.main(["--url", "http://täst.example/"])

    outerr = capsys.readouterr()
    assert "# IDNA pinned" in outerr.out
    assert "169.254.169.254" not in outerr.err
    mock_getaddrinfo.assert_called_once_with(
        "xn--tst-qla.example", 80, type=socket.SOCK_STREAM
    )
    mock_get.assert_called_once_with(
        "http://täst.example/", timeout=30, allow_redirects=False
    )


@patch("socket.getaddrinfo", return_value=[(None, None, None, None, ("8.8.8.8", 0))])
@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(mock_get, _mock_getaddrinfo, capsys, tmp_path):
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
        cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Success!" in outerr.out

    # Ensure any output files are contained under --outdir.
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
