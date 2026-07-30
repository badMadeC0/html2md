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


def test_outdir_existing_file_returns_clear_error(capsys, tmp_path):
    """An existing file passed as --outdir returns a clear preflight error."""
    outdir_file = tmp_path / "not-a-directory"
    outdir_file.write_text("not a directory", encoding="utf-8")

    ret = cli.main(["--url", "http://example.com", "--outdir", str(outdir_file)])

    outerr = capsys.readouterr()
    assert ret == 1
    assert "Error: --outdir must be a directory" in outerr.err
    assert str(outdir_file) in outerr.err


@patch("requests.Session.get")
def test_outdir_creation_failure_returns_error_before_fetch(mock_get, capsys, tmp_path):
    """Output directory creation failures are reported without a traceback."""
    outdir = tmp_path / "blocked"

    with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
        ret = cli.main(["--url", "http://example.com", "--outdir", str(outdir)])

    outerr = capsys.readouterr()
    assert ret == 1
    assert "Error creating output directory" in outerr.err
    assert "Permission denied" in outerr.err
    mock_get.assert_not_called()

def test_url_credentials_redacted_in_stdout_and_filename(capsys, tmp_path):
    """Ensure passwords in URLs are redacted from stdout and not used in filenames."""
    outdir = tmp_path / "output"
    outdir.mkdir()

    with patch("requests.Session.get") as mock_get:
        response = MagicMock()
        response.text = "<h1>dummy</h1>"
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        # A URL without a path means the domain is used for the filename,
        # verifying the password isn't leaked into the filename either.
        url = "http://user:supersecret@example.com"
        cli.main(["--url", url, "--outdir", str(outdir)])

    outerr = capsys.readouterr()

    # The password should not be in the output
    assert "supersecret" not in outerr.out
    assert "supersecret" not in outerr.err

    # The redacted string should be in the output
    assert "user:***@example.com" in outerr.out

    # The output filename should not contain the password
    created_files = list(outdir.glob("*.md"))
    assert len(created_files) == 1
    assert "supersecret" not in created_files[0].name
