"""Tests for the main CLI entry point."""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest
from html2md.cli import main


@pytest.fixture
def mock_dependencies():
    """Mock external network and conversion dependencies."""
    # Since `requests` and `markdownify` might not be installed,
    # we inject mocks into sys.modules
    mock_requests = MagicMock()
    mock_markdownify = MagicMock()

    session_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "<html><body>Fake Content</body></html>"
    mock_response.raise_for_status.return_value = None
    session_instance.get.return_value = mock_response
    mock_requests.Session.return_value = session_instance

    mock_markdownify.markdownify.return_value = "# Fake Content\n\nConverted."

    sys.modules["requests"] = mock_requests
    sys.modules["markdownify"] = mock_markdownify

    yield session_instance, mock_markdownify.markdownify

    # Cleanup sys.modules
    sys.modules.pop("requests", None)
    sys.modules.pop("markdownify", None)


def test_main_batch_success(tmp_path, capsys, mock_dependencies):
    """Test successful batch processing of multiple URLs."""
    session_instance, mock_md = mock_dependencies

    # Setup test file
    batch_file = tmp_path / "urls.txt"
    urls = ["https://example.com/page1", "https://example.com/page2"]
    batch_file.write_text("\n".join(urls), encoding="utf-8")

    ret = main(["--batch", str(batch_file)])

    assert ret == 0

    # Verify Session.get was called twice
    assert session_instance.get.call_count == 2

    # The first argument to get() is the URL
    calls = [call.args[0] for call in session_instance.get.call_args_list]
    assert calls == urls

    # Verify markdownify was called twice
    assert mock_md.call_count == 2

    # Verify output
    captured = capsys.readouterr()
    assert "Processing URL: https://example.com/page1" in captured.out
    assert "Processing URL: https://example.com/page2" in captured.out
    assert "# Fake Content" in captured.out


def test_main_batch_file_not_found(tmp_path, capsys, mock_dependencies):
    """Test batch processing with a nonexistent file."""
    nonexistent_file = tmp_path / "does_not_exist.txt"

    ret = main(["--batch", str(nonexistent_file)])

    assert ret == 1

    captured = capsys.readouterr()
    assert f"Error: Batch file not found: {nonexistent_file}" in captured.out


def test_main_batch_with_outdir(tmp_path, capsys, mock_dependencies):
    """Test batch processing with an output directory."""
    session_instance, mock_md = mock_dependencies

    # Setup test file
    batch_file = tmp_path / "urls.txt"
    urls = ["https://example.com/page1", "https://example.com/page2"]
    batch_file.write_text("\n".join(urls), encoding="utf-8")

    outdir = tmp_path / "output_dir"

    ret = main(["--batch", str(batch_file), "--outdir", str(outdir)])

    assert ret == 0

    # Verify outputs
    assert outdir.exists()
    assert outdir.is_dir()

    files = list(outdir.glob("*.md"))
    assert len(files) == 2

    file_names = {f.name for f in files}
    assert "page1.md" in file_names
    assert "page2.md" in file_names

    # Verify content
    for file in files:
        content = file.read_text(encoding="utf-8")
        assert content == "# Fake Content\n\nConverted."

    captured = capsys.readouterr()
    assert f"Success! Saved to: {outdir / 'page1.md'}" in captured.out
    assert f"Success! Saved to: {outdir / 'page2.md'}" in captured.out
