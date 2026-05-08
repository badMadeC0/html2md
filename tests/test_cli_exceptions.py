"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import tempfile
import requests  # type: ignore[import-untyped]
from html2md.cli import FAILURE, MAX_DOWNLOAD_SIZE, main


def make_stream_response(body=b"<h1>Hello</h1>", headers=None):
    """Create a response mock compatible with streamed downloads."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = headers or {}
    mock_resp.encoding = 'utf-8'
    mock_resp.apparent_encoding = 'utf-8'
    mock_resp.iter_content.return_value = [body]
    return mock_resp


class TestCliExceptions(unittest.TestCase):
    """Unit tests for CLI network, file, and path-containment error handling."""

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
                mock_get.return_value = make_stream_response()

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
                mock_get.return_value = make_stream_response()

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.path.exists', return_value=True):
                        import builtins
                        real_open = builtins.open
                        def custom_open(file, *args, **kwargs):
                            if str(file).endswith('.md'):
                                return MagicMock()
                            return real_open(file, *args, **kwargs)
                        with patch('builtins.open', side_effect=custom_open) as mock_open:
                            def fake_realpath(path):
                                if str(path).endswith('.md'):
                                    return '/tmp/outside/a.md'
                                return '/tmp/out'

                            with patch('os.path.realpath', side_effect=fake_realpath):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                            output = captured_stderr.getvalue()
                            self.assertIn("Output path escapes output directory", output)
                            # Verify open was not called for our expected markdown file
                            for call in mock_open.call_args_list:
                                self.assertFalse(str(call[0][0]).endswith('.md'))

    def test_oversized_content_length_returns_failure(self):
        """Test that advertised oversized responses propagate a failing status."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_resp = make_stream_response(
                    headers={'Content-Length': str(MAX_DOWNLOAD_SIZE + 1)}
                )
                mock_get.return_value = mock_resp

                status = main(['--url', 'http://example.com/large'])

                self.assertEqual(status, FAILURE)
                self.assertIn(
                    "Content exceeds maximum allowed size", captured_stderr.getvalue()
                )
                mock_resp.close.assert_called_once()

    def test_oversized_stream_returns_failure(self):
        """Test that streamed oversized responses propagate a failing status."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_resp = make_stream_response(
                    body=b'a' * (MAX_DOWNLOAD_SIZE + 1),
                    headers={'Content-Length': 'not-a-number'},
                )
                mock_get.return_value = mock_resp

                status = main(['--url', 'http://example.com/large'])

                self.assertEqual(status, FAILURE)
                self.assertIn(
                    "Content exceeds maximum allowed size", captured_stderr.getvalue()
                )
                mock_resp.close.assert_called_once()

    def test_batch_aggregates_oversized_url_failure(self):
        """Test that batch mode returns failure if any URL is oversized."""
        captured_stderr = io.StringIO()
        with tempfile.NamedTemporaryFile('w', encoding='utf-8') as batch_file:
            batch_file.write('http://example.com/small\n')
            batch_file.write('http://example.com/large\n')
            batch_file.flush()

            with patch('sys.stderr', captured_stderr):
                with patch('requests.Session.get') as mock_get:
                    small_resp = make_stream_response(body=b'<h1>Small</h1>')
                    large_resp = make_stream_response(
                        headers={'Content-Length': str(MAX_DOWNLOAD_SIZE + 1)}
                    )
                    mock_get.side_effect = [small_resp, large_resp]

                    status = main(['--batch', batch_file.name])

                    self.assertEqual(status, FAILURE)
                    self.assertIn(
                        "Content exceeds maximum allowed size",
                        captured_stderr.getvalue(),
                    )
                    self.assertEqual(mock_get.call_count, 2)
                    small_resp.close.assert_called_once()
                    large_resp.close.assert_called_once()
