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
    response.iter_content.return_value = [b"<h1>dummy</h1>"]
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


def test_outdir_existing_file_returns_clear_error(capsys, tmp_path):
    """An existing file passed as --outdir returns a clear preflight error."""
    outdir_file = tmp_path / "not-a-directory"
    outdir_file.write_text("not a directory", encoding="utf-8")

    ret = cli.main(["--url", "http://example.com", "--outdir", str(outdir_file)])

    outerr = capsys.readouterr()
    assert ret == 1
    assert "Error: --outdir must be a directory" in outerr.err
    assert str(outdir_file) in outerr.err


@patch("requests.Session.get")
def test_outdir_creation_failure_returns_error_before_fetch(mock_get, capsys, tmp_path):
    """Output directory creation failures are reported without a traceback."""
    outdir = tmp_path / "blocked"

    with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
        ret = cli.main(["--url", "http://example.com", "--outdir", str(outdir)])

    outerr = capsys.readouterr()
    assert ret == 1
    assert "Error creating output directory" in outerr.err
    assert "Permission denied" in outerr.err
    mock_get.assert_not_called()

import socket
@patch("socket.getaddrinfo")
def test_process_url_blocks_ssrf(mock_gethostbyname, capsys):
    """Ensure that SSRF payloads are blocked."""
    mock_gethostbyname.return_value = [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", 0))]

    ret = cli.main(["--url", "http://localhost:8080/"])
    outerr = capsys.readouterr()

    assert ret == 1
    assert "resolves to a forbidden internal IP address" in outerr.err

import socket
@patch("socket.getaddrinfo")
@patch("requests.Session.get")
def test_process_url_blocks_ssrf_via_redirect(mock_get, mock_gethostbyname, capsys):
    """Ensure that SSRF payloads via redirects are blocked."""
    # First request goes to a safe IP
    def fake_getaddrinfo(hostname, port):
        if hostname == "safe.com":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0))]
        elif hostname == "internal.local":
            return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.1", 0))]
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.2.3.4", 0))]
    mock_gethostbyname.side_effect = fake_getaddrinfo

    response = MagicMock()
    response.is_redirect = True
    response.headers = {"Location": "http://internal.local/"}
    mock_get.return_value = response

    ret = cli.main(["--url", "http://safe.com/"])
    outerr = capsys.readouterr()

    assert ret == 1
    assert "Redirect resolves to a forbidden internal IP address" in outerr.err
