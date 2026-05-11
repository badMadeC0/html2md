"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import pytest

from html2md import cli

try:
    import requests
except ImportError:
    requests = None


@pytest.mark.skipif(requests is None, reason="requests not installed")
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


@pytest.mark.skipif(requests is None, reason="requests not installed")
@patch("requests.Session.get")
def test_ssrf_protection_rejects_local_ips(mock_get, capsys, tmp_path):
    """Local and private IP addresses should be rejected for security reasons."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    urls = [
        "http://127.0.0.1/test",
        "http://192.168.1.1/admin",
        "http://10.0.0.5/api",
        "http://localhost/secret",
        "http://[::1]/",
        "http://169.254.169.254/latest/meta-data/",
    ]

    for url in urls:
        cli.main(["--url", url, "--outdir", str(outdir)])
        outerr = capsys.readouterr()
        assert "Error: Request to local or private IP address" in outerr.err

    mock_get.assert_not_called()


@pytest.mark.skipif(requests is None, reason="requests not installed")
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
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()
