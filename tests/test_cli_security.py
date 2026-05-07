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
    assert list(
        outdir.rglob("*.md")
    ), "No markdown files were created in the output directory."
    assert secret_file.read_text(encoding="utf-8") == "secret content"
    assert not (tmp_path / "secret.txt.md").exists()


@patch("os.path.realpath")
@patch("html2md.cli.os.path.normcase")
def test_is_safe_path_security(mock_normcase, mock_realpath):
    """Test is_safe_path comprehensively for traversal and prefix-collision."""
    from html2md.cli import is_safe_path
    import os

    # Mock behavior for basic Unix paths
    mock_realpath.side_effect = lambda x: x
    mock_normcase.side_effect = lambda x: x

    # Prefix collision attack
    assert not is_safe_path("/tmp/foo", f"/tmp/foobar{os.sep}file.md")
    # Exact match
    assert is_safe_path("/tmp/foo", "/tmp/foo")
    # Subdirectory match
    assert is_safe_path("/tmp/foo", f"/tmp/foo{os.sep}file.md")

    # Simulating os.path.realpath behavior for path traversal
    # Traversal should resolve to outside the directory
    mock_realpath.side_effect = lambda x: "/tmp/bar/file.md" if ".." in x else x
    assert not is_safe_path("/tmp/foo", f"/tmp/foo/../../bar{os.sep}file.md")

    # Windows different drives
    def mock_realpath_win(x):
        return x

    mock_realpath.side_effect = mock_realpath_win

    def mock_normcase_win(x):
        return x.lower().replace("/", "\\")

    mock_normcase.side_effect = mock_normcase_win

    # Test Windows drive mismatch using ValueError to simulate os.path.realpath/commonpath if we were using it,
    # but since is_safe_path uses normcase + startswith, diff drives naturally fail startswith!
    # Let's ensure C:\foo and D:\foo\file.md fails
    # Windows path separator logic: os.sep is '/' on linux, so we need to patch os.sep for the test to truly simulate Windows,
    # or just test the logic directly. The logic in is_safe_path relies on os.sep.

    with patch("html2md.cli.os.sep", "\\\\"):
        assert not is_safe_path("C:\\\\foo", "D:\\\\foo\\\\file.md")
        assert is_safe_path("C:\\\\foo", "C:\\\\foo\\\\file.md")
        assert is_safe_path(
            "C:\\\\foo", "c:\\\\foo\\\\file.md"
        )  # normcase makes it match
        assert not is_safe_path("C:\\\\foo", "C:\\\\foobar\\\\file.md")
