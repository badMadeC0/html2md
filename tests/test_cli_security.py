import socket

"""Security-focused tests for CLI URL and output path handling."""

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
        "http://10.0.0.1/",
        "http://192.168.1.1/",
        "http://172.16.0.1/",
        "http://169.254.169.254/",
        "http://0.0.0.0/",
        "http://[::1]/",
    ],
)
@patch("requests.Session.get")
def test_ssrf_protection_rejects_unsafe(mock_get, capsys, url):
    """Ensure that SSRF protection rejects loopback, private, and reserved IPs."""
    cli.main(["--url", url])
    outerr = capsys.readouterr()
    assert "resolves to an unsafe/internal IP address" in outerr.err
    mock_get.assert_not_called()


@patch("requests.Session.get")
def test_ssrf_protection_accepts_safe(mock_get, capsys):
    """Ensure that SSRF protection accepts safe external IPs."""
    # We use a mocked request because we don't want to hit real network in tests
    mock_response = MagicMock()
    mock_response.text = "<h1>Safe</h1>"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    # Need to mock socket.getaddrinfo to avoid actual DNS lookup and make it deterministic
    with patch("socket.getaddrinfo") as mock_dns:
        # Mocking getaddrinfo to return a safe global IP for example.com
        # Return format: [(family, type, proto, canonname, sockaddr), ...]
        mock_dns.return_value = [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))
        ]

        cli.main(["--url", "http://example.com/"])

    outerr = capsys.readouterr()
    # It should pass the safety check, mock_get should be called
    mock_get.assert_called_once()
    assert "resolves to an unsafe/internal IP address" not in outerr.err
