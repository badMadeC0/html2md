"""Security-focused tests for CLI URL and output path handling."""

import socket
from unittest.mock import MagicMock, call, patch

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
def test_process_url_blocks_unsafe_redirect(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """Redirect targets must be SSRF-checked before they are fetched."""

    def fake_getaddrinfo(hostname, *_args, **_kwargs):
        ip = "169.254.169.254" if hostname == "169.254.169.254" else "93.184.216.34"
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 0))]

    mock_getaddrinfo.side_effect = fake_getaddrinfo

    redirect = MagicMock()
    redirect.status_code = 302
    redirect.headers = {"Location": "http://169.254.169.254/latest/meta-data/"}
    mock_get.return_value = redirect

    cli.main(["--url", "http://example.com/start", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert (
        "Error: URL 'http://169.254.169.254/latest/meta-data/' resolves to a "
        "non-public IP address."
    ) in outerr.err
    mock_get.assert_called_once_with(
        "http://example.com/start", timeout=30, allow_redirects=False
    )


@patch("html2md.cli.socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_follows_safe_redirect(
    mock_get, mock_getaddrinfo, capsys, tmp_path
):
    """Safe redirect targets should be fetched after validation."""
    mock_getaddrinfo.return_value = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 0))
    ]

    redirect = MagicMock()
    redirect.status_code = 301
    redirect.headers = {"Location": "/final"}

    response = MagicMock()
    response.status_code = 200
    response.headers = {}
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None

    mock_get.side_effect = [redirect, response]

    cli.main(["--url", "http://example.com/start", "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert "Success!" in outerr.out
    assert mock_get.call_args_list == [
        call("http://example.com/start", timeout=30, allow_redirects=False),
        call("http://example.com/final", timeout=30, allow_redirects=False),
    ]
