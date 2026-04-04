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


@pytest.mark.parametrize(
    "url, mock_ip, expected_error",
    [
        ("http://localhost/admin", "127.0.0.1", "Error: Security violation - accessing internal/private IP (127.0.0.1) is prohibited."),
        ("http://127.0.0.1:8080", "127.0.0.1", "Error: Security violation - accessing internal/private IP (127.0.0.1) is prohibited."),
        ("http://169.254.169.254/metadata", "169.254.169.254", "Error: Security violation - accessing internal/private IP (169.254.169.254) is prohibited."),
        ("http://10.0.0.1/internal", "10.0.0.1", "Error: Security violation - accessing internal/private IP (10.0.0.1) is prohibited."),
        ("http://172.16.0.1/", "172.16.0.1", "Error: Security violation - accessing internal/private IP (172.16.0.1) is prohibited."),
        ("http://192.168.1.100/", "192.168.1.100", "Error: Security violation - accessing internal/private IP (192.168.1.100) is prohibited."),
        ("http://[::1]/", "::1", "Error: Security violation - accessing internal/private IP (::1) is prohibited."),
        ("http://[fe80::1%eth0]/", "fe80::1%eth0", "Error: Security violation - accessing internal/private IP (fe80::1) is prohibited."),
        ("http://[fd00::1]/", "fd00::1", "Error: Security violation - accessing internal/private IP (fd00::1) is prohibited."),
    ]
)
@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_ssrf_protection_blocks_internal_ips(mock_get, mock_getaddrinfo, capsys, tmp_path, url, mock_ip, expected_error):
    """SSRF protection blocks requests to internal/private IPs."""
    # socket.getaddrinfo returns a list of tuples: (family, type, proto, canonname, sockaddr)
    mock_getaddrinfo.return_value = [(2, 1, 6, '', (mock_ip, 80))]

    cli.main(["--url", url, "--outdir", str(tmp_path)])

    outerr = capsys.readouterr()
    assert expected_error in outerr.err
    mock_get.assert_not_called()

@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_traversal_like_paths_stay_within_outdir(mock_get, mock_getaddrinfo, capsys, tmp_path):
    """Traversal-like URL paths must never write outside of --outdir."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    secret_file = tmp_path / "secret.txt"
    secret_file.write_text("secret content", encoding="utf-8")

    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response
    mock_getaddrinfo.return_value = [(2, 1, 6, '', ("8.8.8.8", 80))]

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
