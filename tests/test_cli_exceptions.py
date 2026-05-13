"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock
import io
import requests  # type: ignore[import-untyped]
from pathlib import Path
from html2md.cli import main


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
                mock_resp = MagicMock()
                mock_resp.text = "<h1>Hello</h1>"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with (
                        patch('pathlib.Path.exists', return_value=False),
                        patch('pathlib.Path.mkdir'),
                        patch('pathlib.Path.open', side_effect=OSError("Permission denied")),
                    ):
                        try:
                            main(['--url', 'http://example.com', '--outdir', 'dummy'])
                        except (SystemExit, RuntimeError, ValueError) as e:
                            self.fail(f"main raised exception {e}")

                        output = captured_stderr.getvalue()
                        self.assertIn("File error", output)
                        self.assertIn("Permission denied", output)

    def test_outdir_is_file_returns_error(self):
        """Test that --outdir pointing at an existing file returns a non-zero exit code."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with (
                patch('pathlib.Path.exists', return_value=True),
                patch('pathlib.Path.is_dir', return_value=False),
            ):
                result = main(['--url', 'http://example.com', '--outdir', '/tmp/file.txt'])

        assert result != 0
        assert "--outdir must be a directory" in captured_stderr.getvalue()

    def test_outdir_containment_uses_path_aware_check(self):
        """Test that output containment check rejects prefix-matching escapes."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('requests.Session.get') as mock_get:
                mock_resp = MagicMock()
                mock_resp.text = "<h1>Hello</h1>"
                mock_resp.status_code = 200
                mock_get.return_value = mock_resp

                with patch('markdownify.markdownify', return_value="# Hello"):
                    with (
                        patch('pathlib.Path.exists', return_value=True),
                        patch('pathlib.Path.is_dir', return_value=True),
                        patch('pathlib.Path.mkdir'),
                    ):
                        with patch('pathlib.Path.open') as mock_open:
                            def fake_resolve(path):
                                if str(path).endswith('.md'):
                                    return Path('/tmp/outside/a.md')
                                return Path('/tmp/out')

                            with patch('pathlib.Path.resolve', fake_resolve):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                            output = captured_stderr.getvalue()
                            self.assertIn("Output path escapes output directory", output)
                            mock_open.assert_not_called()
