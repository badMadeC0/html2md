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
    response.encoding = "utf-8"
    response.apparent_encoding = "utf-8"
    response.iter_content.return_value = [b"<h1>dummy</h1>"]
    response.raise_for_status.return_value = None
    response.__enter__.return_value = response
    response.__exit__.return_value = None
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
def test_oversize_single_url_fails_without_system_exit(mock_get, capsys):
    """Oversized streamed responses fail single-URL runs without exiting."""
    response = MagicMock()
    response.encoding = "utf-8"
    response.apparent_encoding = "utf-8"
    response.raise_for_status.return_value = None
    response.iter_content.return_value = [b"x" * (10 * 1024 * 1024 + 1)]
    response.__enter__.return_value = response
    response.__exit__.return_value = None
    mock_get.return_value = response

    result = cli.main(["--url", "http://example.com/huge"])

    assert result == 1
    response.__exit__.assert_called_once()
    outerr = capsys.readouterr()
    assert "Response too large" in outerr.err


@patch("requests.Session.get")
def test_oversize_batch_closes_response_and_continues(mock_get, capsys, tmp_path):
    """Oversized batch entries are closed without aborting later URLs."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text(
        "http://example.com/huge\nhttp://example.com/small\n",
        encoding="utf-8",
    )

    huge_response = MagicMock()
    huge_response.encoding = "utf-8"
    huge_response.apparent_encoding = "utf-8"
    huge_response.raise_for_status.return_value = None
    huge_response.iter_content.return_value = [b"x" * (10 * 1024 * 1024 + 1)]
    huge_response.__enter__.return_value = huge_response
    huge_response.__exit__.return_value = None

    small_response = MagicMock()
    small_response.raise_for_status.return_value = None
    small_response.iter_content.return_value = [b"<h1>ok</h1>"]
    small_response.encoding = "utf-8"
    small_response.apparent_encoding = "utf-8"
    small_response.__enter__.return_value = small_response
    small_response.__exit__.return_value = None

    mock_get.side_effect = [huge_response, small_response]

    result = cli.main(["--batch", str(batch_file)])

    assert result == 1
    huge_response.__exit__.assert_called_once()
    assert mock_get.call_count == 2
    outerr = capsys.readouterr()
    assert "Response too large" in outerr.err
    assert "# ok" in outerr.out.lower()
