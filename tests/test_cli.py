"""Tests for CLI module."""

import os
import sys
from unittest.mock import MagicMock, patch

from html2md.cli import main


def test_cli_outdir_creates_directory(tmp_path):
    """Test that specifying --outdir creates the directory if it doesn't exist."""
    # Mock requests and markdownify where they are imported
    mock_requests = MagicMock()
    mock_session_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Hello</h1></body></html>"
    mock_session_instance.get.return_value = mock_response
    mock_requests.Session.return_value = mock_session_instance

    mock_markdownify = MagicMock()
    mock_md = MagicMock(return_value="# Hello\n")
    mock_markdownify.markdownify = mock_md

    outdir = tmp_path / "new_outdir"
    assert not outdir.exists()

    with patch.dict(sys.modules, {"requests": mock_requests, "markdownify": mock_markdownify}):
        # Run the CLI
        argv = ["--url", "http://example.com/testpage", "--outdir", str(outdir)]
        ret = main(argv)

    # Verify success
    assert ret == 0

    # Verify directory was created
    assert outdir.exists()
    assert outdir.is_dir()

    # Verify file was created with correct name based on URL
    expected_file = outdir / "testpage.md"
    assert expected_file.exists()

    # Verify file content
    with open(expected_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert content == "# Hello\n"


def test_cli_outdir_existing_directory(tmp_path):
    """Test that specifying an existing --outdir works correctly without failing."""
    # Mock requests and markdownify
    mock_requests = MagicMock()
    mock_session_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Hello</h1></body></html>"
    mock_session_instance.get.return_value = mock_response
    mock_requests.Session.return_value = mock_session_instance

    mock_markdownify = MagicMock()
    mock_md = MagicMock(return_value="# Hello\n")
    mock_markdownify.markdownify = mock_md

    outdir = tmp_path / "existing_outdir"
    outdir.mkdir()
    assert outdir.exists()

    with patch.dict(sys.modules, {"requests": mock_requests, "markdownify": mock_markdownify}):
        # Run the CLI with a URL that has no path to test filename generation
        argv = ["--url", "http://example.com/", "--outdir", str(outdir)]
        ret = main(argv)

    # Verify success
    assert ret == 0

    # os.path.basename("http://example.com") is "example.com"
    expected_file = outdir / "example.com.md"
    assert expected_file.exists()


def test_cli_outdir_fallback_filename(tmp_path):
    """Test fallback filename when URL has no usable basename."""
    mock_requests = MagicMock()
    mock_session_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "content"
    mock_session_instance.get.return_value = mock_response
    mock_requests.Session.return_value = mock_session_instance

    mock_markdownify = MagicMock()
    mock_md = MagicMock(return_value="content")
    mock_markdownify.markdownify = mock_md

    outdir = tmp_path / "out"

    with patch.dict(sys.modules, {"requests": mock_requests, "markdownify": mock_markdownify}):
        # URL that results in empty string after rstrip('/')
        argv = ["--url", "/", "--outdir", str(outdir)]
        ret = main(argv)

    assert ret == 0
    assert (outdir / "conversion_result.md").exists()
