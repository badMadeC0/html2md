"""Unit tests for the html2md CLI."""

from unittest.mock import MagicMock
import pytest

from html2md.cli import process_url


@pytest.fixture
def mock_session():
    """Mock for requests.Session."""
    session = MagicMock()
    response = MagicMock()
    response.text = "<html><body><h1>Test</h1></body></html>"
    # Ensure raise_for_status doesn't raise anything by default
    response.raise_for_status.return_value = None
    session.get.return_value = response
    return session


@pytest.fixture
def mock_md_func():
    """Mock for markdownify function."""

    def _md_func(text, **kwargs):
        return "# Test\n"

    return MagicMock(side_effect=_md_func)


def test_process_url_happy_path_stdout(mock_session, mock_md_func, capsys):
    """Test successful fetch and markdown conversion, printing to stdout."""
    url = "http://example.com/page"
    process_url(url, mock_session, mock_md_func, outdir=None)

    # Verify session.get was called correctly
    mock_session.get.assert_called_once_with(url, timeout=30)

    # Verify markdownify was called correctly
    mock_md_func.assert_called_once_with(
        "<html><body><h1>Test</h1></body></html>", heading_style="ATX"
    )

    # Verify stdout
    captured = capsys.readouterr()
    assert "Processing URL: http://example.com/page" in captured.out
    assert "Fetching content..." in captured.out
    assert "Converting to Markdown..." in captured.out
    assert "# Test\n" in captured.out


def test_process_url_happy_path_outdir(mock_session, mock_md_func, tmp_path, capsys):
    """Test successful fetch and markdown conversion, saving to outdir."""
    url = "http://example.com/page"
    outdir = tmp_path / "output"

    process_url(url, mock_session, mock_md_func, outdir=str(outdir))

    # Verify the output directory was created
    assert outdir.exists()
    assert outdir.is_dir()

    # Verify the file was created and contains the correct content
    expected_file = outdir / "page.md"
    assert expected_file.exists()
    with open(expected_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "# Test\n"

    # Verify stdout
    captured = capsys.readouterr()
    assert f"Success! Saved to: {expected_file}" in captured.out


def test_process_url_typo_fix(mock_session, mock_md_func):
    """Test fixing a common URL typo (/? -> ?)."""
    url = "http://example.com/?param=value"
    process_url(url, mock_session, mock_md_func, outdir=None)

    # The typo `/?` should be replaced with `?`
    expected_url = "http://example.com?param=value"
    mock_session.get.assert_called_once_with(expected_url, timeout=30)


def test_process_url_session_get_fails(mock_session, mock_md_func, capsys):
    """Test error handling when session.get raises an exception."""
    url = "http://example.com/fail"
    mock_session.get.side_effect = Exception("Connection error")

    process_url(url, mock_session, mock_md_func, outdir=None)

    # Verify the exception was caught and printed
    captured = capsys.readouterr()
    assert "Conversion failed: Connection error" in captured.out

    # Markdownify should not be called
    mock_md_func.assert_not_called()
