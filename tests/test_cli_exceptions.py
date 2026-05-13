"""Tests for html2md CLI exception-handling paths."""
import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import requests  # type: ignore[import-untyped]
from html2md.cli import main
from pathlib import Path

class TestCliExceptions(unittest.TestCase):
    """Test exception paths in the CLI."""

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_missing_dependency(self, mock_stderr):
        """Test handling of missing dependencies."""
        original_import = __builtins__['__import__']
        def mock_import(name, *args, **kwargs):
            if name == 'requests':
                raise ImportError("mocked import error", name="requests")
            return original_import(name, *args, **kwargs)

        with patch('builtins.__import__') as m_import:
            m_import.side_effect = mock_import
            result = main(['--url', 'http://example.com'])
            self.assertEqual(result, 1)
            self.assertIn("Missing dependency requests", mock_stderr.getvalue())

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_invalid_scheme(self, mock_stderr):
        """Test rejection of non-http/https URL schemes."""
        main(['--url', 'ftp://example.com'])
        self.assertIn("Unsupported URL scheme", mock_stderr.getvalue())

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_network_error(self, mock_stderr):
        """Test handling of network exceptions."""
        with patch('requests.Session.get') as mock_get:
            mock_get.side_effect = requests.RequestException("Mock network failure")
            main(['--url', 'http://example.com'])
            self.assertIn("Network error:", mock_stderr.getvalue())

    @patch('sys.stderr', new_callable=io.StringIO)
    def test_file_os_error(self, mock_stderr):
        """Test handling of file I/O exceptions."""
        with patch('requests.Session.get') as mock_get:
            mock_resp = MagicMock()
            mock_resp.text = "<h1>Test</h1>"
            mock_resp.status_code = 200
            mock_get.return_value = mock_resp

            with patch('markdownify.markdownify', return_value="# Test"):
                with (
                    patch('pathlib.Path.exists', return_value=True),
                    patch('pathlib.Path.is_dir', return_value=True),
                    patch('pathlib.Path.open', side_effect=OSError("Mock IO error"))
                ):
                    main(['--url', 'http://example.com', '--outdir', '/tmp'])
                    self.assertIn("File error:", mock_stderr.getvalue())

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
                        original_open = open
                        def mock_open_impl(*args, **kwargs):
                            if str(args[0]).endswith('.mo'):
                                return original_open(*args, **kwargs)
                            return mock_open(read_data='')()
                        with patch('pathlib.Path.open', side_effect=mock_open_impl) as mock_open_call:
                            def fake_resolve(self, strict=False):
                                if str(self).endswith('.md'):
                                    return Path('/tmp/outside/a.md')
                                return Path('/tmp/out')

                            with patch('pathlib.Path.resolve', autospec=True, side_effect=fake_resolve):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                            output = captured_stderr.getvalue()
                            self.assertIn("Output path escapes output directory", output)
