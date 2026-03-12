import unittest
from unittest.mock import patch, MagicMock
import io
import requests
from html2md.cli import main

class TestCliExceptions(unittest.TestCase):
    def test_network_error(self):
        """Test that network errors are caught and printed."""
        # Mock sys.stderr to capture output
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            # Patch requests.Session.get directly
            with patch('requests.Session.get') as mock_get:
                mock_get.side_effect = requests.RequestException("Network unreachable")

                try:
                    main(['--url', 'http://example.com'])
                except Exception as e:
                    self.fail(f"main raised exception {e}")

                output = captured_stderr.getvalue()
                # Expect "Network error: Network unreachable"
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
                    with patch('os.makedirs'), patch('os.path.exists', return_value=False):
                        with patch('builtins.open', side_effect=OSError("Permission denied")):
                             try:
                                 main(['--url', 'http://example.com', '--outdir', 'dummy'])
                             except Exception as e:
                                 self.fail(f"main raised exception {e}")

                             output = captured_stderr.getvalue()
                             # Expect "File error: Permission denied"
                             self.assertIn("File error", output)
                             self.assertIn("Permission denied", output)

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
                    with patch('os.path.exists', return_value=True):
                        # Use target patch so we only mock open in html2md.cli instead of globally builtins.open
                        with patch('html2md.cli.open') as mock_open:
                            def fake_realpath(path):
                                if str(path).endswith('.md'):
                                    return '/tmp/outside/a.md'
                                return '/tmp/out'

                            with patch('os.path.realpath', side_effect=fake_realpath):
                                # Just run main, we've patched realpath so it will fail the path escape check
                                # and print to stderr, which we are capturing
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                            output = captured_stderr.getvalue()
                            self.assertIn("Output path escapes output directory", output)
                            mock_open.assert_not_called()
