"""Security-focused tests for CLI URL and output path handling."""

from unittest.mock import MagicMock, patch
import pytest
import requests

from html2md import cli


class StreamingResponse(requests.Response):
    """requests.Response test double that fails if .text is used."""

    def __init__(self, chunks, status_error=None):
        super().__init__()
        self.status_code = 200
        self.encoding = "utf-8"
        self._chunks = chunks
        self._status_error = status_error
        self.closed = False

    @property
    def text(self):
        raise AssertionError("response.text should not be used for real responses")

    def iter_content(self, chunk_size=1, decode_unicode=False):
        return iter(self._chunks)

    def raise_for_status(self):
        if self._status_error is not None:
            raise self._status_error

    def close(self):
        self.closed = True


@patch("requests.Session.get")
def test_real_response_streaming_enforces_download_cap(mock_get, capsys):
    """Real requests responses must stream so oversized bodies are rejected."""
    max_size = 10 * 1024 * 1024
    response = StreamingResponse([b"x" * (max_size + 1)])
    mock_get.return_value = response

    with patch("markdownify.markdownify") as markdownify:
        cli.main(["--url", "http://example.com/large"])

    outerr = capsys.readouterr()
    assert (
        f"Downloaded content exceeds maximum allowed size ({max_size} bytes)"
        in outerr.err
    )
    assert response.closed
    markdownify.assert_not_called()


@patch("requests.Session.get")
def test_real_response_closes_when_status_check_fails(mock_get, capsys):
    """Streamed responses must close even if raise_for_status raises."""
    response = StreamingResponse([], requests.HTTPError("500 Server Error"))
    mock_get.return_value = response

    cli.main(["--url", "http://example.com/fail"])

    outerr = capsys.readouterr()
    assert "Network error: 500 Server Error" in outerr.err
    assert response.closed


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
