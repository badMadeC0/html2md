import sys
import os
import unittest
import builtins
import logging
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Ensure src is in sys.path
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

import html2md.cli

class TestGetUniqueFilepath(unittest.TestCase):
    """Tests for get_unique_filepath helper function."""

    def test_file_does_not_exist(self):
        """Test when file does not exist, it returns the original path."""
        with patch('os.path.exists', return_value=False):
            result = html2md.cli.get_unique_filepath('test.md')
            self.assertEqual(result, 'test.md')

    def test_file_exists_once(self):
        """Test when file exists, it appends (1)."""
        # side_effect: first call (original) returns True, second (with 1) returns False
        with patch('os.path.exists', side_effect=[True, False]):
            result = html2md.cli.get_unique_filepath('test.md')
            self.assertEqual(result, 'test (1).md')

    def test_file_exists_multiple(self):
        """Test when file exists multiple times, it increments the counter."""
        # side_effect: original -> True, (1) -> True, (2) -> False
        with patch('os.path.exists', side_effect=[True, True, False]):
            result = html2md.cli.get_unique_filepath('test.md')
            self.assertEqual(result, 'test (2).md')


class TestMain(unittest.TestCase):
    """Tests for main CLI function."""

    def setUp(self):
        # Mocks for dependencies that are imported inside main
        self.mock_requests = MagicMock()
        self.mock_markdownify = MagicMock()
        self.mock_bs4 = MagicMock()
        self.mock_reportlab_platypus = MagicMock()
        self.mock_reportlab_styles = MagicMock()

        self.modules_patch = patch.dict(sys.modules, {
            'requests': self.mock_requests,
            'markdownify': self.mock_markdownify,
            'bs4': self.mock_bs4,
            'reportlab.platypus': self.mock_reportlab_platypus,
            'reportlab.lib.styles': self.mock_reportlab_styles,
        })
        self.modules_patch.start()

        # Create a temporary directory for file output tests
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        self.modules_patch.stop()
        shutil.rmtree(self.test_dir)

    def test_help_only(self):
        """Test --help-only argument."""
        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            ret = html2md.cli.main(['--help-only'])
            self.assertEqual(ret, 0)
            mock_print_help.assert_called_once()

    def test_no_args(self):
        """Test running with no arguments."""
        with patch('argparse.ArgumentParser.print_help') as mock_print_help:
            ret = html2md.cli.main([])
            self.assertEqual(ret, 0)
            mock_print_help.assert_called_once()

    def test_missing_dependencies(self):
        """Test behavior when dependencies are missing."""
        # Stop the setUp patch so we can apply a failing one
        self.modules_patch.stop()

        original_import = builtins.__import__

        def side_effect(name, *args, **kwargs):
            if name == 'requests':
                raise ImportError("No module named 'requests'", name='requests')
            return original_import(name, *args, **kwargs)

        # We need to ensure 'requests' is not in sys.modules so the import is triggered
        with patch.dict(sys.modules):
            if 'requests' in sys.modules:
                del sys.modules['requests']

            with patch('builtins.__import__', side_effect=side_effect):
                # Capture logging
                with self.assertLogs(level='ERROR') as log:
                    ret = html2md.cli.main(['--url', 'http://example.com'])
                    self.assertEqual(ret, 1)
                    # Check if expected error message is in logs
                    self.assertTrue(any("Missing dependency requests" in m for m in log.output))

        self.modules_patch.start()

    def test_simple_conversion_stdout(self):
        """Test simple URL conversion printing to stdout."""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.text = '<html><body><h1>Hello</h1></body></html>'
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = '# Hello'

        with patch('builtins.print') as mock_print:
            ret = html2md.cli.main(['--url', 'http://example.com'])

            self.assertEqual(ret, 0)
            self.mock_requests.Session.return_value.get.assert_called_with('http://example.com', timeout=30)
            self.mock_markdownify.markdownify.assert_called()
            mock_print.assert_called_with('# Hello')

    def test_file_output(self):
        """Test conversion saving to file."""
        mock_response = MagicMock()
        mock_response.text = '<html>Content</html>'
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = 'Content'

        out_dir = os.path.join(self.test_dir, 'output')

        ret = html2md.cli.main(['--url', 'http://example.com/foo', '--outdir', out_dir])

        self.assertEqual(ret, 0)
        self.assertTrue(os.path.isdir(out_dir))

        # Check for generated file
        expected_file = os.path.join(out_dir, 'foo.md')
        self.assertTrue(os.path.exists(expected_file))

        with open(expected_file, 'r') as f:
            content = f.read()
        self.assertEqual(content, 'Content')

    def test_all_formats(self):
        """Test --all-formats option."""
        mock_response = MagicMock()
        mock_response.text = '<html>Content</html>'
        self.mock_requests.Session.return_value.get.return_value = mock_response
        self.mock_markdownify.markdownify.return_value = 'Content'

        # Mock BeautifulSoup for TXT extraction
        mock_soup = MagicMock()
        mock_soup.get_text.return_value = 'Content Text'
        self.mock_bs4.BeautifulSoup.return_value = mock_soup

        out_dir = os.path.join(self.test_dir, 'all_formats')

        ret = html2md.cli.main(['--url', 'http://example.com', '--outdir', out_dir, '--all-formats'])

        self.assertEqual(ret, 0)

        expected_base = 'example.com'

        self.assertTrue(os.path.exists(os.path.join(out_dir, f'{expected_base}.md')))
        self.assertTrue(os.path.exists(os.path.join(out_dir, f'{expected_base}.txt')))

        # PDF is handled by reportlab mock, so no file is created.
        # We verify that the code *attempted* to create it.
        pdf_path = os.path.join(out_dir, f'{expected_base}.pdf')
        self.mock_reportlab_platypus.SimpleDocTemplate.assert_called_with(pdf_path)
        self.mock_reportlab_platypus.SimpleDocTemplate.return_value.build.assert_called()

    def test_main_content_extraction(self):
        """Test --main-content option."""
        mock_response = MagicMock()
        mock_response.text = '<html><body><nav>Menu</nav><main>Main Content</main></body></html>'
        self.mock_requests.Session.return_value.get.return_value = mock_response

        mock_soup = MagicMock()
        mock_main_tag = MagicMock()
        mock_main_tag.__str__.return_value = '<main>Main Content</main>'
        mock_soup.find.return_value = mock_main_tag
        self.mock_bs4.BeautifulSoup.return_value = mock_soup

        with patch('builtins.print'):
            html2md.cli.main(['--url', 'http://example.com', '--main-content'])

            self.mock_bs4.BeautifulSoup.assert_called()
            mock_soup.find.assert_called_with('main')
            self.mock_markdownify.markdownify.assert_called_with('<main>Main Content</main>', heading_style="ATX")

    def test_batch_processing(self):
        """Test --batch processing."""
        # Create a real batch file
        batch_file = os.path.join(self.test_dir, 'urls.txt')
        with open(batch_file, 'w') as f:
            f.write("http://a.com\nhttp://b.com")

        # Setup conversion mocks
        mock_response = MagicMock()
        mock_response.text = 'html'
        self.mock_requests.Session.return_value.get.return_value = mock_response

        with patch('builtins.print'):
            ret = html2md.cli.main(['--batch', batch_file])

            self.assertEqual(ret, 0)
            # Should have called get twice
            self.assertEqual(self.mock_requests.Session.return_value.get.call_count, 2)
            self.mock_requests.Session.return_value.get.assert_any_call('http://a.com', timeout=30)
            self.mock_requests.Session.return_value.get.assert_any_call('http://b.com', timeout=30)

    def test_url_correction(self):
        """Test that URLs with /? are corrected."""
        mock_response = MagicMock()
        mock_response.text = 'html'
        self.mock_requests.Session.return_value.get.return_value = mock_response

        with patch('builtins.print'):
            html2md.cli.main(['--url', 'http://example.com/?q=1'])

            # The actual call should be with ? instead of /?
            self.mock_requests.Session.return_value.get.assert_called_with('http://example.com?q=1', timeout=30)

if __name__ == '__main__':
    unittest.main()
