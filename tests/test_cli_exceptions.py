"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


def make_streaming_response(chunks, encoding="utf-8"):
    """Create a mocked streaming HTTP response."""
    response = MagicMock()
    response.raise_for_status.return_value = None
    response.iter_content.return_value = chunks
    response.encoding = encoding
    response.apparent_encoding = encoding
    return response


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
                mock_resp = make_streaming_response([b"<h1>Hello</h1>"])
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                        import argparse
                        argparse.ArgumentParser() # pre-initialize
                        import gettext
                        gettext.dgettext('argparse', 'positional arguments') # Pre-load translations

                        import builtins
                        original_open = builtins.open
                        def custom_open(file, *args, **kwargs):
                            if "conversion_result" in str(file) or "dummy" in str(file):
                                raise OSError("Permission denied")
                            return original_open(file, *args, **kwargs)

                        with patch('builtins.open', side_effect=custom_open):
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
                mock_resp = make_streaming_response([b"<h1>Hello</h1>"])
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.path.exists', return_value=True):
                        import argparse
                        argparse.ArgumentParser() # pre-initialize
                        import gettext
                        gettext.dgettext('argparse', 'positional arguments') # Pre-load translations

                        import builtins
                        original_open = builtins.open
                        def custom_open(file, *args, **kwargs):
                            if "conversion_result" in str(file) or "dummy" in str(file):
                                raise OSError("Permission denied")
                            return original_open(file, *args, **kwargs)

                        with patch('builtins.open', side_effect=custom_open):
                            def fake_realpath(path):
                                if str(path).endswith('.md'):
                                    return '/tmp/outside/a.md'
                                return '/tmp/out'

                            with patch('os.path.realpath', side_effect=fake_realpath):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                        output = captured_stderr.getvalue()
                        self.assertIn("Output path escapes output directory", output)

    def test_oversized_response_skips_batch_item_without_exiting(self):
        """Test oversized downloads do not terminate subsequent batch items."""
        max_size = 10 * 1024 * 1024
        oversized_resp = make_streaming_response([b"x" * max_size, b"x"])
        ok_resp = make_streaming_response([b"<h1>Hello</h1>"])

        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get', side_effect=[oversized_resp, ok_resp]):
                with patch('markdownify.markdownify', return_value="# Hello") as mock_md:
                    with patch('os.path.exists', return_value=True):
                        with patch('html2md.cli.open', create=True) as mock_open:
                            mock_open.return_value.__enter__.return_value.__iter__.return_value = [
                                'http://example.com/too-large\n',
                                'http://example.com/ok\n',
                            ]

                            try:
                                exit_code = main(['--batch', 'urls.txt'])
                            except (SystemExit, RuntimeError, ValueError) as e:
                                self.fail(f"main raised exception {e}")

        self.assertEqual(exit_code, 1)
        self.assertIn("Response too large", captured_stderr.getvalue())
        oversized_resp.close.assert_called_once()
        ok_resp.close.assert_called_once()
        mock_md.assert_called_once()
