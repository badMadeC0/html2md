"""Tests for html2md CLI error-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os
import requests  # type: ignore[import-untyped]

# Ensure src is in path before importing the local package.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

import html2md.cli  # pylint: disable=wrong-import-position  # type: ignore[import-untyped]


class TestCliError(unittest.TestCase):
    """Unit tests for CLI network and conversion error handling."""

    def test_cli_conversion_request_failure(self):
        """Test that requests.get failure is caught and printed."""

        # Configure requests mock to fail
        # Use a real RequestException so the except block catches it
        mock_requests = MagicMock()
        mock_requests.RequestException = requests.RequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_session.get.side_effect = requests.RequestException("Network error")

        mock_markdownify = MagicMock()

        # Capture stderr
        captured_stderr = io.StringIO()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('sys.stderr', captured_stderr):
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        self.assertIn("Network error", output)

    def test_cli_conversion_markdownify_failure(self):
        """Test that markdownify failure is caught and printed."""

        mock_requests = MagicMock()
        # We need RequestException to be valid for the except clause
        mock_requests.RequestException = requests.RequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = "<html></html>"
        mock_session.get.return_value = mock_response

        mock_markdownify = MagicMock()
        # Mocking the module attribute access
        mock_markdownify.markdownify.side_effect = Exception("Parse error")

        captured_stderr = io.StringIO()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('sys.stderr', captured_stderr):
                try:
                    html2md.cli.main(['--url', 'http://example.com'])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

        output = captured_stderr.getvalue()
        # The code catches Exception and prints "Conversion failed: {e}"
        self.assertIn("Conversion failed", output)
        self.assertIn("Parse error", output)


class StreamingResponse(requests.Response):
    """Response test double that fails if .text is used before streaming."""

    def __init__(self, chunks, status_code=200):
        super().__init__()
        self._chunks = chunks
        self.status_code = status_code
        self.encoding = "utf-8"
        self.closed = False
        self.text_accessed = False

    @property
    def text(self):  # pylint: disable=missing-docstring
        self.text_accessed = True
        raise AssertionError("response.text should not be read for real responses")

    def iter_content(
        self, chunk_size=1, decode_unicode=False
    ):  # pylint: disable=unused-argument
        yield from self._chunks

    def close(self):
        self.closed = True


class TestCliStreamingResponses(unittest.TestCase):
    """Unit tests for streamed response cleanup and size limits."""

    def test_real_response_streams_without_reading_text(self):
        """Real requests.Response objects should stream instead of using .text."""
        response = StreamingResponse([b"<h1>Hello</h1>"])

        with patch('requests.Session.get', return_value=response):
            with patch('markdownify.markdownify', return_value="# Hello") as mock_md:
                html2md.cli.main(['--url', 'http://example.com'])

        self.assertFalse(response.text_accessed)
        self.assertTrue(response.closed)
        mock_md.assert_called_once_with("<h1>Hello</h1>", heading_style="ATX")

    def test_oversized_real_response_is_closed_before_conversion(self):
        """Oversized real streamed responses should be closed and not converted."""
        response = StreamingResponse([b"x" * (html2md.cli.MAX_DOWNLOAD_SIZE + 1)])
        captured_stderr = io.StringIO()

        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', return_value=response):
                with patch('markdownify.markdownify') as mock_md:
                    html2md.cli.main(['--url', 'http://example.com'])

        self.assertIn(
            "Downloaded content exceeds maximum allowed size",
            captured_stderr.getvalue(),
        )
        self.assertFalse(response.text_accessed)
        self.assertTrue(response.closed)
        mock_md.assert_not_called()

    def test_response_that_reaches_exact_download_cap_is_converted(self):
        """Real responses at the download cap should still be converted."""
        response = StreamingResponse([b"x" * html2md.cli.MAX_DOWNLOAD_SIZE])

        with patch('requests.Session.get', return_value=response):
            with patch('markdownify.markdownify', return_value="converted") as mock_md:
                html2md.cli.main(['--url', 'http://example.com'])

        self.assertFalse(response.text_accessed)
        self.assertTrue(response.closed)
        mock_md.assert_called_once_with(
            "x" * html2md.cli.MAX_DOWNLOAD_SIZE,
            heading_style="ATX",
        )

    def test_error_response_is_closed_when_status_check_raises(self):
        """HTTP error responses should close even if raise_for_status() raises."""
        response = StreamingResponse([], status_code=500)
        captured_stderr = io.StringIO()

        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', return_value=response):
                html2md.cli.main(['--url', 'http://example.com'])

        self.assertIn("Network error", captured_stderr.getvalue())
        self.assertTrue(response.closed)

    def test_status_error_closes_mocked_streamed_response(self):
        """Mocked streamed responses should close when status checks fail."""
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("bad status")
        captured_stderr = io.StringIO()

        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', return_value=response):
                html2md.cli.main(['--url', 'http://example.com'])

        self.assertIn("Network error: bad status", captured_stderr.getvalue())
        response.close.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
