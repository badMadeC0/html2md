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
    assert list(outdir.rglob("*.md")), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()


@patch("requests.Session.get")
def test_dos_content_length_limit(mock_get, capsys, tmp_path):
    """Test that responses with a Content-Length exceeding the limit are rejected."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    response = MagicMock()
    # 21 MB, which exceeds the 20 MB limit
    response.headers = {'content-length': str(21 * 1024 * 1024)}
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/large", "--outdir", str(outdir)])
    outerr = capsys.readouterr()

    assert "exceeds maximum allowed size" in outerr.err
    assert "20971520 bytes" in outerr.err  # 20 * 1024 * 1024
    response.close.assert_called_once()


@patch("requests.Session.get")
def test_dos_stream_size_limit(mock_get, capsys, tmp_path):
    """Test that responses without Content-Length but exceeding limit during streaming are rejected."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    response = MagicMock()
    response.headers = {}
    response.raise_for_status.return_value = None

    # Simulate streaming 21 chunks of 1MB, exceeding the 20MB limit
    def mock_iter_content(chunk_size=8192):
        for _ in range(21):
            yield b"a" * (1024 * 1024)

    response.iter_content = mock_iter_content
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/infinite", "--outdir", str(outdir)])
    outerr = capsys.readouterr()

    assert "Downloaded content exceeded maximum allowed size" in outerr.err
    response.close.assert_called_once()
