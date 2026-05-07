"""Tests for html2md CLI exception-handling paths."""
import io
import unittest
from unittest.mock import MagicMock, mock_open, patch

import requests  # type: ignore[import-untyped]

from html2md.cli import main


def make_stream_response(chunks=None, encoding="utf-8", apparent_encoding="utf-8"):
    """Create a response mock that supports streamed context-manager usage."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.encoding = encoding
    mock_resp.apparent_encoding = apparent_encoding
    mock_resp.iter_content.return_value = chunks or [b"<h1>Hello</h1>"]
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
                mock_get.return_value = make_stream_response()

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with patch('os.makedirs'), patch(
                        'os.path.exists', return_value=False
                    ):
                        with patch(
                            'html2md.cli.open',
                            side_effect=OSError("Permission denied"),
                            create=True,
                        ):
                            try:
                                main([
                                    '--url', 'http://example.com',
                                    '--outdir', 'dummy',
                                ])
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
                        output_open = mock_open()
                        with patch('html2md.cli.open', output_open, create=True):
                            def fake_realpath(path):
                                if str(path).endswith('.md'):
                                    return '/tmp/outside/a.md'
                                return '/tmp/out'

                            with patch('os.path.realpath', side_effect=fake_realpath):
                                main([
                                    '--url', 'http://example.com/a',
                                    '--outdir', '/tmp/out',
                                ])

                        output = captured_stderr.getvalue()
                        self.assertIn("Output path escapes output directory", output)
                        output_open.assert_not_called()

    def test_oversized_response_skips_conversion_without_system_exit(self):
        """Oversized streamed downloads should return an error without exiting."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_resp = make_stream_response(
                    chunks=[b"a" * (10 * 1024 * 1024), b"b"]
                )
                mock_get.return_value = mock_resp

                with patch('markdownify.markdownify') as mock_md:
                    try:
                        result = main(['--url', 'http://example.com'])
                    except SystemExit as e:
                        self.fail(f"main raised SystemExit {e}")

                self.assertEqual(result, 1)
                self.assertIn("Response too large", captured_stderr.getvalue())
                mock_md.assert_not_called()
                mock_resp.__exit__.assert_called_once()

    def test_streamed_decode_uses_apparent_encoding_when_charset_missing(self):
        """Missing charset should use Requests-style apparent encoding fallback."""
        word = "café"
        captured_stdout = io.StringIO()
        with patch('sys.stdout', captured_stdout):
            with patch('requests.Session.get') as mock_get:
                mock_get.return_value = make_stream_response(
                    chunks=[f"<p>{word}</p>".encode('iso-8859-1')],
                    encoding=None,
                    apparent_encoding='iso-8859-1',
                )

                with patch(
                    'markdownify.markdownify',
                    side_effect=lambda html, **_: html,
                ) as mock_md:
                    result = main(['--url', 'http://example.com'])

        self.assertEqual(result, 0)
        mock_md.assert_called_once()
        self.assertIn(word, mock_md.call_args.args[0])
        self.assertIn(word, captured_stdout.getvalue())

    def test_invalid_charset_label_falls_back_without_failing(self):
        """Invalid charset labels should fall back like response.text."""
        with patch('requests.Session.get') as mock_get:
            mock_get.return_value = make_stream_response(
                chunks=["<p>ok</p>".encode('utf-8')],
                encoding='not-a-real-codec',
                apparent_encoding='utf-8',
            )

            with patch(
                'markdownify.markdownify',
                side_effect=lambda html, **_: html,
            ) as mock_md:
                result = main(['--url', 'http://example.com'])

        self.assertEqual(result, 0)
        self.assertIn("ok", mock_md.call_args.args[0])

    def test_batch_continues_after_oversized_response(self):
        """An oversized batch item should not prevent later URLs from processing."""
        responses = [
            make_stream_response(chunks=[b"a" * (10 * 1024 * 1024), b"b"]),
            make_stream_response(chunks=[b"<h1>Second</h1>"]),
        ]
        batch_data = "http://example.com/too-large\nhttp://example.com/second\n"

        with patch('os.path.exists', return_value=True), \
                patch(
                    'html2md.cli.open',
                    mock_open(read_data=batch_data),
                    create=True,
                ), \
                patch('requests.Session.get', side_effect=responses) as mock_get, \
                patch('markdownify.markdownify', return_value="# Second") as mock_md:
            result = main(['--batch', 'urls.txt'])

        self.assertEqual(result, 1)
        self.assertEqual(mock_get.call_count, 2)
        mock_md.assert_called_once()
