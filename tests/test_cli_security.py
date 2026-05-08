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


@patch("requests.Session.get")
def test_streaming_oversize_response_is_closed(mock_get, capsys):
    """Oversized streamed responses are closed on early abort."""
    response = MagicMock()
    response.headers = {}
    response.encoding = "utf-8"
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [b"x" * (10 * 1024 * 1024 + 1)]
    mock_get.return_value = response

    with patch("markdownify.markdownify") as mock_markdownify:
        cli.main(["--url", "http://example.com/oversized"])

    outerr = capsys.readouterr()
    assert "Error: Content exceeds maximum allowed size (10MB)." in outerr.err
    response.close.assert_called_once_with()
    mock_markdownify.assert_not_called()
