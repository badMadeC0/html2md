"""Tests for CLI batch processing."""

import os
import sys
from unittest.mock import MagicMock, patch
import pytest

from html2md.cli import main

def test_batch_file_not_found(capsys):
    """Test batch processing with a missing file."""
    # We need to mock the imports so it doesn't fail on Missing dependency first
    with patch.dict('sys.modules', {'requests': MagicMock(), 'markdownify': MagicMock()}):
        result = main(['--batch', 'nonexistent_file_12345.txt'])

    assert result == 1

    captured = capsys.readouterr()
    assert "Error: Batch file not found: nonexistent_file_12345.txt" in captured.out

def test_batch_processing_success(tmp_path, capsys):
    """Test batch processing with valid URLs."""
    # Create a batch file
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text("http://example.com/1\n\nhttp://example.com/2\n", encoding='utf-8')

    # Mock requests and markdownify
    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Test</h1></body></html>"
    mock_session.get.return_value = mock_response

    mock_md = MagicMock()
    mock_md.return_value = "# Test"

    # We need to patch sys.modules because cli.py imports them inside the function
    with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': MagicMock(markdownify=mock_md)}):
        result = main(['--batch', str(batch_file)])

    assert result == 0

    captured = capsys.readouterr()
    assert "Processing URL: http://example.com/1" in captured.out
    assert "Processing URL: http://example.com/2" in captured.out
    assert "Fetching content..." in captured.out
    assert "Converting to Markdown..." in captured.out
    assert "# Test" in captured.out

    # Assert session.get was called correctly
    assert mock_session.get.call_count == 2
    mock_session.get.assert_any_call("http://example.com/1", timeout=30)
    mock_session.get.assert_any_call("http://example.com/2", timeout=30)

    # Assert md was called correctly
    assert mock_md.call_count == 2
    mock_md.assert_any_call(mock_response.text, heading_style="ATX")

def test_batch_processing_failure(tmp_path, capsys):
    """Test batch processing when an exception occurs during conversion."""
    # Create a batch file
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text("http://example.com/fail\n", encoding='utf-8')

    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    # Make session.get raise an exception
    mock_session.get.side_effect = Exception("Network error")

    with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': MagicMock()}):
        result = main(['--batch', str(batch_file)])

    assert result == 0

    captured = capsys.readouterr()
    assert "Processing URL: http://example.com/fail" in captured.out
    assert "Fetching content..." in captured.out
    assert "Conversion failed: Network error" in captured.out

def test_batch_with_outdir(tmp_path, capsys):
    """Test batch processing with an output directory."""
    # Create a batch file
    batch_file = tmp_path / "urls.txt"
    batch_file.write_text("http://example.com/page1\nhttp://example.com/page2\n", encoding='utf-8')

    outdir = tmp_path / "out"

    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    mock_response = MagicMock()
    mock_response.text = "<html><body><h1>Test</h1></body></html>"
    mock_session.get.return_value = mock_response

    mock_md = MagicMock()
    mock_md.return_value = "# Test"

    with patch.dict('sys.modules', {'requests': mock_requests, 'markdownify': MagicMock(markdownify=mock_md)}):
        result = main(['--batch', str(batch_file), '--outdir', str(outdir)])

    assert result == 0

    # Check that files were created
    assert outdir.exists()
    assert (outdir / "page1.md").exists()
    assert (outdir / "page2.md").exists()

    assert (outdir / "page1.md").read_text(encoding='utf-8') == "# Test"
    assert (outdir / "page2.md").read_text(encoding='utf-8') == "# Test"

def test_import_error(capsys):
    """Test that missing dependencies are reported."""
    # Make sure requests is actually missing
    with patch.dict('sys.modules', {'requests': None}):
        result = main(['--batch', 'dummy.txt'])

    assert result == 1

    captured = capsys.readouterr()
    assert "Error: Missing dependency" in captured.out
    assert "Please run: pip install requests markdownify" in captured.out
