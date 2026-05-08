"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import pytest

from html2md import cli


def mock_stream_response(body=b"<h1>dummy</h1>", encoding="utf-8", headers=None):
    """Create a streamed response mock for CLI URL-fetch tests."""
    response = MagicMock()
    response.headers = headers or {}
    response.encoding = encoding
    response.apparent_encoding = encoding or "utf-8"
    response.iter_content.return_value = [body]
    response.raise_for_status.return_value = None
    return response


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

    mock_get.return_value = mock_stream_response()

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
def test_streamed_response_uses_apparent_encoding(mock_get, capsys):
    """Legacy pages without charset headers use Requests' detected encoding."""
    mock_get.return_value = mock_stream_response(
        b"<p>caf\xe9</p>", encoding=None, headers={}
    )
    mock_get.return_value.apparent_encoding = "windows-1252"

    status = cli.main(["--url", "http://example.com/legacy"])

    outerr = capsys.readouterr()
    assert status == 0
    assert "café" in outerr.out


@patch("requests.Session.get")
def test_oversized_content_length_returns_nonzero_and_closes(mock_get, capsys):
    """Oversized responses fail the CLI and release the streamed response."""
    mock_get.return_value = mock_stream_response(
        b"", headers={"Content-Length": str(10 * 1024 * 1024 + 1)}
    )

    status = cli.main(["--url", "http://example.com/huge"])

    outerr = capsys.readouterr()
    assert status == 1
    assert "Content exceeds maximum allowed size" in outerr.err
    mock_get.return_value.close.assert_called_once()


@patch("requests.Session.get")
def test_oversized_stream_returns_nonzero_and_closes(mock_get, capsys):
    """Responses that exceed the limit while streaming fail and are closed."""
    mock_get.return_value = mock_stream_response(headers={})
    mock_get.return_value.iter_content.return_value = [
        b"x" * (10 * 1024 * 1024),
        b"x",
    ]

    status = cli.main(["--url", "http://example.com/huge-stream"])

    outerr = capsys.readouterr()
    assert status == 1
    assert "Content exceeds maximum allowed size" in outerr.err
    mock_get.return_value.close.assert_called_once()
