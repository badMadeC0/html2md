"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main


def make_stream_response(content: bytes, encoding=None, apparent_encoding=None):
    """Create a minimal streamed response mock for URL conversion tests."""

    class StreamResponse:
        """Tiny response stand-in that can fail if apparent_encoding is read."""

        headers = {}

        def __init__(self):
            self.encoding = encoding
            self._apparent_encoding = apparent_encoding
            self.raise_for_status = MagicMock(return_value=None)
            self.iter_content = MagicMock(return_value=[content])

        @property
        def apparent_encoding(self):
            if isinstance(self._apparent_encoding, Exception):
                raise self._apparent_encoding
            return self._apparent_encoding

    return StreamResponse()


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
                mock_resp = make_stream_response(b"<h1>Hello</h1>", encoding="utf-8")
                mock_get.return_value = mock_resp

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
                mock_resp = make_stream_response(b"<h1>Hello</h1>", encoding="utf-8")
                mock_get.return_value = mock_resp

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

    def test_uses_detected_encoding_for_streamed_response(self):
        """Collected bytes should provide the fallback encoding for legacy HTML."""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value = make_stream_response(
                b"<p>\x93Hello\x94</p>",
                encoding=None,
                apparent_encoding=RuntimeError("stream consumed"),
            )

            with patch(
                'requests.compat.chardet.detect',
                return_value={'encoding': 'Windows-1252'},
            ):
                with patch(
                    'markdownify.markdownify',
                    return_value="converted",
                ) as mock_md:
                    main(['--url', 'http://example.com'])

            mock_md.assert_called_once()
            html_arg = mock_md.call_args.args[0]
            self.assertIn("“Hello”", html_arg)

    def test_invalid_response_encoding_falls_back_to_replacement_decode(self):
        """Malformed charset names should not fail conversion."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_get.return_value = make_stream_response(
                    b"<p>\x93Hello\x94</p>",
                    encoding="bogus-charset",
                )

                with patch('markdownify.markdownify', return_value="converted") as mock_md:
                    main(['--url', 'http://example.com'])

        mock_md.assert_called_once()
        self.assertNotIn("Conversion failed", captured_stderr.getvalue())

