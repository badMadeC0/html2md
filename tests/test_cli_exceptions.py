"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


class TestCliExceptions(unittest.TestCase):
    """Unit tests for CLI network, file, and path-containment error handling."""

    @staticmethod
    def _mock_response(chunks=None, headers=None):
        """Build a response mock compatible with streamed downloads."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = headers or {}
        mock_resp.encoding = 'utf-8'
        mock_resp.iter_content.return_value = chunks or [b"<h1>Hello</h1>"]
        return mock_resp

    def test_network_error(self):
        """Test that network errors are caught and printed."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_get.side_effect = requests.RequestException("Network unreachable")

                try:
                    main(['--url', 'http://example.com'])
                except (SystemExit, RuntimeError, ValueError) as e:
                    self.fail(f"main raised exception {e}")

                output = captured_stderr.getvalue()
                self.assertIn("Network error", output)
                self.assertIn("Network unreachable", output)

    def test_file_error(self):
        """Test that file I/O errors are caught and printed."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_get.return_value = self._mock_response()

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                        with patch('builtins.open', side_effect=OSError("Permission denied")):
                            try:
                                main(['--url', 'http://example.com', '--outdir', 'dummy'])
                            except (SystemExit, RuntimeError, ValueError) as e:
                                self.fail(f"main raised exception {e}")

                            output = captured_stderr.getvalue()
                            self.assertIn("File error", output)
                            self.assertIn("Permission denied", output)

    def test_outdir_containment_uses_path_aware_check(self):
        """Test that output containment check rejects prefix-matching escapes."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_get.return_value = self._mock_response()

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.path.exists', return_value=True):
                        with patch('html2md.cli.open', create=True) as mock_open:
                            def fake_realpath(path):
                                if str(path).endswith('.md'):
                                    return '/tmp/outside/a.md'
                                return '/tmp/out'

                            with patch('os.path.realpath', side_effect=fake_realpath):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                            output = captured_stderr.getvalue()
                            self.assertIn("Output path escapes output directory", output)
                            mock_open.assert_not_called()

    def test_rejects_oversized_content_length_and_closes_response(self):
        """Test that oversized Content-Length is rejected and the response is closed."""
        max_size = 10 * 1024 * 1024
        mock_resp = self._mock_response(headers={'Content-Length': str(max_size + 1)})
        captured_stderr = io.StringIO()

        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', return_value=mock_resp):
                with patch('markdownify.markdownify') as mock_markdownify:
                    main(['--url', 'http://example.com'])

        output = captured_stderr.getvalue()
        self.assertIn("Content-Length exceeds maximum allowed size", output)
        mock_resp.iter_content.assert_not_called()
        mock_resp.close.assert_called_once()
        mock_markdownify.assert_not_called()

    def test_rejects_midstream_oversize_and_closes_response(self):
        """Test that streaming stops when downloaded content exceeds the size limit."""
        max_size = 10 * 1024 * 1024
        chunks = [b'a' * max_size, b'b']
        mock_resp = self._mock_response(chunks=chunks)
        captured_stderr = io.StringIO()

        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', return_value=mock_resp):
                with patch('markdownify.markdownify') as mock_markdownify:
                    main(['--url', 'http://example.com'])

        output = captured_stderr.getvalue()
        self.assertIn("Downloaded content exceeds maximum allowed size", output)
        mock_resp.close.assert_called_once()
        mock_markdownify.assert_not_called()
