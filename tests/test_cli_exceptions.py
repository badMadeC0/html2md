"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


def mock_stream_response(html=b"<h1>Hello</h1>", encoding="utf-8", headers=None):
    """Create a context-manager response mock for streamed CLI downloads."""
    mock_resp = MagicMock()
    mock_resp.headers = headers or {}
    mock_resp.encoding = encoding
    mock_resp.apparent_encoding = encoding or "utf-8"
    mock_resp.iter_content.return_value = [html]
    mock_resp.raise_for_status.return_value = None
    mock_resp.__enter__.return_value = mock_resp
    mock_resp.__exit__.return_value = None
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
                mock_get.return_value = mock_stream_response()

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
                mock_get.return_value = mock_stream_response()

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
