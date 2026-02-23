import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import io
import tempfile
from contextlib import redirect_stdout

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html2md.cli import main

class TestCliMock(unittest.TestCase):
    def setUp(self):
        # Create mocks for dependencies
        self.mock_requests = MagicMock()
        self.mock_markdownify = MagicMock()

        # Setup session mock
        self.mock_session = MagicMock()
        self.mock_requests.Session.return_value = self.mock_session

        # Setup markdownify mock
        self.mock_markdownify.markdownify = MagicMock(return_value="# Mocked Markdown")

        # We need to simulate the module structure 'markdownify.markdownify'
        # The import is 'from markdownify import markdownify as md'
        # If we return a MagicMock for the module, accessing .markdownify on it returns another MagicMock (default)
        # We want that inner mock to be our configured one.
        self.mock_markdownify.markdownify = MagicMock(return_value="# Mocked Markdown")


    def test_help_only(self):
        """Test that --help-only prints help and exits with 0."""
        f = io.StringIO()
        with redirect_stdout(f):
            ret = main(['--help-only'])

        output = f.getvalue()
        self.assertEqual(ret, 0)
        self.assertIn('Convert HTML URL to Markdown', output)

    def test_missing_dependencies(self):
        """Test behavior when dependencies are missing."""
        # Ensure dependencies import fails by setting them to None in sys.modules
        # This overrides even if they are installed in the environment.
        with patch.dict(sys.modules, {'requests': None, 'markdownify': None}):
            f = io.StringIO()
            with redirect_stdout(f):
                ret = main(['--url', 'http://example.com'])

            output = f.getvalue()
            self.assertEqual(ret, 1)
            self.assertIn('Missing dependency', output)

    def test_url_success(self):
        """Test successful URL conversion."""
        modules = {
            'requests': self.mock_requests,
            'markdownify': self.mock_markdownify
        }

        with patch.dict(sys.modules, modules):
            mock_response = MagicMock()
            mock_response.text = "<html><body><h1>Test</h1></body></html>"
            mock_response.raise_for_status.return_value = None
            self.mock_session.get.return_value = mock_response

            f = io.StringIO()
            with redirect_stdout(f):
                ret = main(['--url', 'http://example.com'])

            output = f.getvalue()
            self.assertEqual(ret, 0)
            self.assertIn('Processing URL: http://example.com', output)
            self.assertIn('Converting to Markdown...', output)
            # Check mock calls
            self.mock_session.get.assert_called_with('http://example.com', timeout=30)
            # The 'markdownify' called is self.mock_markdownify.markdownify
            self.mock_markdownify.markdownify.assert_called()

    def test_url_file_output(self):
        """Test output to file using real temporary directory."""
        modules = {
            'requests': self.mock_requests,
            'markdownify': self.mock_markdownify
        }

        with patch.dict(sys.modules, modules):
            mock_response = MagicMock()
            mock_response.text = "content"
            self.mock_session.get.return_value = mock_response

            with tempfile.TemporaryDirectory() as tmpdir:
                f = io.StringIO()
                with redirect_stdout(f):
                    ret = main(['--url', 'http://example.com/page', '--outdir', tmpdir])

                self.assertEqual(ret, 0)

                # Check file creation
                expected_file = os.path.join(tmpdir, 'page.md')
                self.assertTrue(os.path.exists(expected_file))

                with open(expected_file, 'r', encoding='utf-8') as f_read:
                    content = f_read.read()
                    self.assertEqual(content, "# Mocked Markdown")

                output = f.getvalue()
                self.assertIn(f"Success! Saved to: {expected_file}", output)

    def test_batch_processing(self):
        """Test batch processing from file using real temporary file."""
        modules = {
            'requests': self.mock_requests,
            'markdownify': self.mock_markdownify
        }

        with patch.dict(sys.modules, modules):
            mock_response = MagicMock()
            mock_response.text = "content"
            self.mock_session.get.return_value = mock_response

            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
                tmp.write("http://a.com\nhttp://b.com")
                tmp_path = tmp.name

            try:
                f = io.StringIO()
                with redirect_stdout(f):
                    ret = main(['--batch', tmp_path])

                output = f.getvalue()
                self.assertEqual(ret, 0)
                self.assertIn('Processing URL: http://a.com', output)
                self.assertIn('Processing URL: http://b.com', output)
                self.assertEqual(self.mock_session.get.call_count, 2)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    def test_request_exception(self):
        """Test error handling during request."""
        modules = {
            'requests': self.mock_requests,
            'markdownify': self.mock_markdownify
        }

        with patch.dict(sys.modules, modules):
            self.mock_session.get.side_effect = Exception("Network Error")

            f = io.StringIO()
            with redirect_stdout(f):
                ret = main(['--url', 'http://fail.com'])

            output = f.getvalue()
            self.assertIn('Conversion failed: Network Error', output)
            self.assertEqual(ret, 0)

if __name__ == '__main__':
    unittest.main()
