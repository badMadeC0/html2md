import unittest
from unittest.mock import patch, MagicMock
import io
import requests
import builtins
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
                        # Don't mock builtins.open globally before argparse is initialized
                        # because argparse may load gettext translations and open .mo files
                        # We only need to mock open during the file write part, but it's simpler
                        # to just let the code run. Since fake_realpath makes it look like it escapes,
                        # the open() call will never be reached anyway.
                        # We just mock it locally when main runs.
                        def fake_realpath(path):
                            if str(path).endswith('.md'):
                                return '/tmp/outside/a.md'
                            return '/tmp/out'

                        with patch('os.path.realpath', side_effect=fake_realpath):
                            original_open = builtins.open
                            def custom_open(*args, **kwargs):
                                if args and 'conversion_result.md' in args[0] or args[0].endswith('.md'):
                                    raise AssertionError("open called when it shouldn't be")
                                return original_open(*args, **kwargs)

                            with patch('builtins.open', side_effect=custom_open):
                                main(['--url', 'http://example.com/a', '--outdir', '/tmp/out'])

                        output = captured_stderr.getvalue()
                        self.assertIn("Output path escapes output directory", output)
