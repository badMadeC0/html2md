"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import pytest

from html2md import cli


def mock_response(body=b"<h1>dummy</h1>"):
    """Create a streamed response mock for CLI URL-fetch tests."""
    response = MagicMock()
    response.headers = {}
    response.encoding = "utf-8"
    response.apparent_encoding = "utf-8"
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

    mock_get.return_value = mock_response()

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


class StreamingResponse:
    """Minimal streamed response test double for CLI download handling."""

    def __init__(self, chunks, headers=None, encoding="utf-8"):
        self._chunks = chunks
        self.headers = headers or {}
        self.encoding = encoding
        self.closed = False

    def raise_for_status(self):
        """Simulate a successful response."""

    def iter_content(self, chunk_size=8192):  # pylint: disable=unused-argument
        """Yield configured response chunks."""
        yield from self._chunks

    def close(self):
        """Record that the streamed response was released."""
        self.closed = True


@patch("requests.Session.get")
def test_header_oversize_response_is_closed(mock_get, capsys):
    """Header-size aborts must close streamed responses promptly."""
    response = StreamingResponse(
        chunks=[],
        headers={"Content-Length": str((10 * 1024 * 1024) + 1)},
    )
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/large"])

    outerr = capsys.readouterr()
    assert "Content exceeds maximum allowed size" in outerr.err
    assert response.closed is True


@patch("requests.Session.get")
def test_streaming_oversize_response_is_closed(mock_get, capsys):
    """Streaming-size aborts must close streamed responses promptly."""
    response = StreamingResponse(chunks=[b"a" * ((10 * 1024 * 1024) + 1)])
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/large"])

    outerr = capsys.readouterr()
    assert "Content exceeds maximum allowed size" in outerr.err
    assert response.closed is True
