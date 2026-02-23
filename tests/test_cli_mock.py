"""Tests for CLI using mocks."""

import sys
import unittest
import os
from unittest.mock import MagicMock, patch, mock_open
import html2md.cli

class TestCliMain(unittest.TestCase):
    """Test the CLI main function."""

    @patch('argparse.ArgumentParser.print_help')
    def test_help_only(self, mock_print_help):
        """Test that --help-only prints help and returns 0."""
        ret = html2md.cli.main(['--help-only'])
        self.assertEqual(ret, 0)
        mock_print_help.assert_called_once()

    @patch('argparse.ArgumentParser.print_help')
    def test_no_args(self, mock_print_help):
        """Test that no arguments prints help and returns 0."""
        ret = html2md.cli.main([])
        self.assertEqual(ret, 0)
        mock_print_help.assert_called_once()

    def test_url_processing(self):
        """Test processing a single URL."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = '<html><body><h1>Hello</h1></body></html>'
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock(return_value='# Hello')
        mock_markdownify_module.markdownify = mock_md

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('builtins.print') as mock_print:
                ret = html2md.cli.main(['--url', 'http://example.com'])

                self.assertEqual(ret, 0)

                # Verify requests
                mock_requests.Session.assert_called_once()
                mock_session.get.assert_called_with('http://example.com', timeout=30)
                mock_response.raise_for_status.assert_called_once()

                # Verify markdownify
                mock_md.assert_called_with(mock_response.text, heading_style="ATX")

                # Verify output printed
                mock_print.assert_any_call('# Hello')

    def test_url_typo_fix(self):
        """Test that URL typo '/?' is fixed."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_markdownify_module.markdownify = MagicMock(return_value='result')

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('builtins.print'):
                html2md.cli.main(['--url', 'http://example.com/?q=1'])
                mock_session.get.assert_called_with('http://example.com?q=1', timeout=30)

    def test_outdir_processing(self):
        """Test processing with --outdir."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = 'content'
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock(return_value='# Content')
        mock_markdownify_module.markdownify = mock_md

        real_open = open
        mock_file = mock_open()

        def open_side_effect(file, mode='r', *args, **kwargs):
            if isinstance(file, str) and file.startswith(test_outdir):
                return mock_file(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('os.path.exists', return_value=False) as mock_exists:
                with patch('os.makedirs') as mock_makedirs:
                    with patch('builtins.open', side_effect=open_side_effect):
                        with patch('builtins.print'):
                            html2md.cli.main(['--url', 'http://example.com/foo', '--outdir', 'out'])

                            mock_makedirs.assert_called_with('out')
                            mock_file.assert_called_with(os.path.join('out', 'foo.md'), 'w', encoding='utf-8')
                            mock_file().write.assert_called_with('# Content')

    def test_outdir_default_filename(self):
        """Test processing with --outdir and default filename."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = 'content'
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock(return_value='# Content')
        mock_markdownify_module.markdownify = mock_md

        real_open = open
        mock_file = mock_open()

        def open_side_effect(file, mode='r', *args, **kwargs):
            if isinstance(file, str) and file.startswith('out'):
                return mock_file(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', side_effect=open_side_effect):
                    with patch('builtins.print'):
                        html2md.cli.main(['--url', 'http://example.com/', '--outdir', 'out'])

                        mock_file.assert_called_with(os.path.join('out', 'example.com.md'), 'w', encoding='utf-8')

    def test_outdir_fallback_filename(self):
        """Test processing with --outdir and fallback filename."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = 'content'
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock(return_value='# Content')
        mock_markdownify_module.markdownify = mock_md

        real_open = open
        mock_file = mock_open()

        def open_side_effect(file, mode='r', *args, **kwargs):
            # The 'out' directory name is used in the CLI arguments and assertions.
            # Ideally, this value would be a variable defined at the test function level.
            expected_outdir_prefix = 'out'
            if isinstance(file, str) and file.startswith(expected_outdir_prefix):
                return mock_file(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', side_effect=open_side_effect):
                    with patch('builtins.print'):
                        # Using '?query' to force empty basename from split('?')[0] which is empty string
                        html2md.cli.main(['--url', '?query', '--outdir', 'out'])

                        mock_file.assert_called_with(os.path.join('out', 'conversion_result.md'), 'w', encoding='utf-8')

    def test_batch_processing(self):
        """Test processing with --batch."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_response = MagicMock()
        mock_response.text = 'content'
        mock_session.get.return_value = mock_response

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock(return_value='# Content')
        mock_markdownify_module.markdownify = mock_md

        batch_content = "http://example.com/1\nhttp://example.com/2\n"

        real_open = open
        mock_file = mock_open(read_data=batch_content)

        def open_side_effect(file, mode='r', *args, **kwargs):
            if file == 'urls.txt':
                return mock_file(file, mode, *args, **kwargs)
            return real_open(file, mode, *args, **kwargs)

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', side_effect=open_side_effect):
                    with patch('builtins.print'):
                        html2md.cli.main(['--batch', 'urls.txt'])

                        self.assertEqual(mock_session.get.call_count, 2)
                        mock_session.get.assert_any_call('http://example.com/1', timeout=30)
                        mock_session.get.assert_any_call('http://example.com/2', timeout=30)

    def test_missing_dependency(self):
        """Test missing dependency ImportError."""
        # Using sys.modules with None triggers ImportError on import
        with patch.dict(sys.modules, {'requests': None}):
             with patch('builtins.print') as mock_print:
                 ret = html2md.cli.main(['--url', 'http://example.com'])

                 self.assertEqual(ret, 1)
                 # Expect "Error: Missing dependency"
                 args_list = mock_print.call_args_list
                 # Join all calls to check message
                 messages = [call.args[0] for call in args_list if call.args]
                 self.assertTrue(any("Error: Missing dependency" in m for m in messages))

    def test_request_error(self):
        """Test handling of request exception."""
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        # Simulate request exception. Using Exception for generic handler or specifically request exception.
        # The code catches generic Exception.
        mock_session.get.side_effect = Exception("Network Error")

        mock_markdownify_module = MagicMock()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('builtins.print') as mock_print:
                html2md.cli.main(['--url', 'http://example.com'])

                # Should catch exception and print error
                mock_print.assert_any_call("Conversion failed: Network Error")

    def test_batch_file_not_found(self):
        """Test batch file not found."""
        mock_requests = MagicMock()
        mock_markdownify_module = MagicMock()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            with patch('os.path.exists', return_value=False):
                with patch('builtins.print') as mock_print:
                    ret = html2md.cli.main(['--batch', 'missing.txt'])
                    self.assertEqual(ret, 1)
                    mock_print.assert_called_with("Error: Batch file not found: missing.txt")

if __name__ == '__main__':
    unittest.main()
