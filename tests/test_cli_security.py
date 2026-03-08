"""Security tests for the CLI."""

import io
import os
import sys
import pytest
from unittest.mock import patch, MagicMock

def test_download_size_limit_exceeded_content_length(capsys):
    """Test that download is aborted if Content-Length exceeds the maximum limit."""
    mock_response = MagicMock()
    mock_response.headers = {'Content-Length': str(11 * 1024 * 1024)} # 11 MB

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch.dict('sys.modules', {'requests': MagicMock(), 'markdownify': MagicMock()}):
        import requests
        with patch.object(requests, 'Session', return_value=mock_session):
            from html2md.cli import main as cli_main
            cli_main(['--url', 'http://example.com/huge-file'])

    captured = capsys.readouterr()
    assert "Conversion failed" in captured.out
    assert "Content-Length exceeds maximum allowed size" in captured.out


def test_download_size_limit_exceeded_stream(capsys):
    """Test that download is aborted if streamed content exceeds the maximum limit."""
    mock_response = MagicMock()
    mock_response.headers = {}

    # Create a generator that yields 2MB chunks, 6 times (12MB total)
    def iter_content(chunk_size):
        for _ in range(6):
            yield b"a" * (2 * 1024 * 1024)

    mock_response.iter_content = iter_content
    mock_response.encoding = 'utf-8'

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch.dict('sys.modules', {'requests': MagicMock(), 'markdownify': MagicMock()}):
        import requests
        with patch.object(requests, 'Session', return_value=mock_session):
            from html2md.cli import main as cli_main
            cli_main(['--url', 'http://example.com/huge-stream'])

    captured = capsys.readouterr()
    assert "Conversion failed" in captured.out
    assert "Response exceeds maximum allowed size" in captured.out


def test_download_size_limit_ok(capsys):
    """Test that a normal download within limits succeeds."""
    mock_response = MagicMock()
    mock_response.headers = {'Content-Length': str(1024)}

    def iter_content(chunk_size):
        yield b"<h1>Hello World</h1>"

    mock_response.iter_content = iter_content
    mock_response.encoding = 'utf-8'

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with patch.dict('sys.modules', {'requests': MagicMock(), 'markdownify': MagicMock()}):
        import requests
        import markdownify
        markdownify.markdownify.return_value = '# Hello World'
        with patch.object(requests, 'Session', return_value=mock_session):
            from html2md.cli import main as cli_main
            cli_main(['--url', 'http://example.com/normal-file'])

    captured = capsys.readouterr()
    assert "Fetching content..." in captured.out
    assert "Converting to Markdown..." in captured.out
