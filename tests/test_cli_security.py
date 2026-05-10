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
def test_whole_page_option_includes_header_and_footer(mock_get, capsys):
    """--whole-page includes document chrome that defaults omit."""
    response = MagicMock()
    response.text = (
        "<header><h1>Site Header</h1></header>"
        "<main><p>Main body</p></main>"
        "<footer>Site Footer</footer>"
    )
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    rc = cli.main(["--url", "https://example.com", "--whole-page"])
    outerr = capsys.readouterr()

    assert rc == 0
    assert "Site Header" in outerr.out
    assert "Main body" in outerr.out
    assert "Site Footer" in outerr.out


@patch("requests.Session.get")
def test_default_url_conversion_omits_header_and_footer(mock_get, capsys):
    """The default GUI/CLI URL conversion excludes page chrome."""
    response = MagicMock()
    response.text = (
        "<header><h1>Site Header</h1></header>"
        "<main><p>Main body</p></main>"
        "<footer>Site Footer</footer>"
    )
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    rc = cli.main(["--url", "https://example.com"])
    outerr = capsys.readouterr()

    assert rc == 0
    assert "Site Header" not in outerr.out
    assert "Main body" in outerr.out
    assert "Site Footer" not in outerr.out
