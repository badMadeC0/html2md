"""Tests for html2md CLI exception-handling paths."""
import io
import unittest
from unittest.mock import MagicMock, patch

import requests  # type: ignore[import-untyped]

from html2md import cli
from html2md.cli import main


def public_addrinfo():
    """Build a deterministic public getaddrinfo response for tests."""
    return [(cli.socket.AF_INET, cli.socket.SOCK_STREAM, 6, "", ("93.184.216.34", 80))]


class TestCliExceptions(unittest.TestCase):
    """Unit tests for CLI network, file, and path-containment error handling."""

    def test_network_error(self):
        """Test that network errors are caught and printed."""
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            with patch('html2md.cli.socket.getaddrinfo', return_value=public_addrinfo()):
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
            with patch('html2md.cli.socket.getaddrinfo', return_value=public_addrinfo()):
                with patch('requests.Session.get') as mock_get:
                    mock_resp = MagicMock()
                    mock_resp.text = "<h1>Hello</h1>"
                    mock_resp.status_code = 200
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
            with patch('html2md.cli.socket.getaddrinfo', return_value=public_addrinfo()):
                with patch('requests.Session.get') as mock_get:
                    mock_resp = MagicMock()
                    mock_resp.text = "<h1>Hello</h1>"
                    mock_resp.status_code = 200
                    mock_get.return_value = mock_resp

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
