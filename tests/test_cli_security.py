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
def test_gui_flags_are_supported_for_url_conversion(mock_get, capsys, tmp_path):
    """GUI-only flags must be accepted by the packaged CLI."""
    response = MagicMock()
    response.text = "<html><body><nav>Skip me</nav><main><h1>Keep me</h1></main></body></html>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    result = cli.main([
        "--url",
        "http://example.com/page",
        "--outdir",
        str(tmp_path),
        "--all-formats",
        "--main-content",
    ])

    outerr = capsys.readouterr()
    assert result == 0
    assert "Success!" in outerr.out
    assert (tmp_path / "page.md").exists()
    assert (tmp_path / "page.txt").exists()
    assert (tmp_path / "page.pdf").exists()
    assert "Keep me" in (tmp_path / "page.md").read_text(encoding="utf-8")
    assert "Skip me" not in (tmp_path / "page.md").read_text(encoding="utf-8")
    mock_get.assert_called_once_with("http://example.com/page", timeout=30)
