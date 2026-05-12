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


@pytest.mark.parametrize(
    "args, expected_text, unexpected_text",
    [
        ([], "Body", "Header"),
        (["--whole-page"], "Header", None),
    ],
)
@patch("requests.Session.get")
def test_whole_page_option_controls_gui_batch_conversion(
    mock_get, tmp_path, args, expected_text, unexpected_text
):
    """GUI batch mode --whole-page should drive conversion behavior."""
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text("https://example.com/article\n", encoding="utf-8")
    outdir = tmp_path / "out"

    response = MagicMock()
    response.text = "<header>Header</header><main>Body</main><footer>Footer</footer>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response

    rc = cli.main([
        "--batch", str(batch_file),
        "--outdir", str(outdir),
        *args,
    ])

    assert rc == 0
    mock_get.assert_called_once_with("https://example.com/article", timeout=30)
    output = (outdir / "article.md").read_text(encoding="utf-8")
    assert expected_text in output
    if unexpected_text is not None:
        assert unexpected_text not in output
        assert "Footer" not in output
