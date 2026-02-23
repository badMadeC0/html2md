import os
import sys
import unittest
from unittest.mock import MagicMock, patch
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from html2md.cli import main

class TestCliSecurity(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_markdownify_strip_arguments(self):
        # Create mocks
        mock_requests = MagicMock()
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '<html><script>alert(1)</script></html>'
        mock_response.raise_for_status.return_value = None
        mock_session.get.return_value = mock_response
        mock_requests.Session.return_value = mock_session

        mock_markdownify_module = MagicMock()
        mock_md = MagicMock()
        mock_md.return_value = "converted content"
        mock_markdownify_module.markdownify = mock_md

        # Patch sys.modules to inject mocks
        # We need to patch 'requests' and 'markdownify' so that the imports inside main() pick them up
        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify_module}):
            # Run CLI
            url = 'http://example.com/test'
            argv = ['--url', url, '--outdir', self.test_dir]

            ret = main(argv)

            self.assertEqual(ret, 0, "CLI returned non-zero exit code")

            # Verify markdownify was called with strip argument
            args, kwargs = mock_md.call_args
            self.assertEqual(args[0], mock_response.text)
            self.assertEqual(kwargs.get('heading_style'), 'ATX')

            # The crucial check:
            strip_arg = kwargs.get('strip')

            self.assertIsNotNone(strip_arg, "markdownify called without 'strip' argument")
            # Explicitly define the list of tags to check for, to match what's in the CLI code
            STRIP_TAGS = ['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta']
            for tag in STRIP_TAGS:
                self.assertIn(tag, strip_arg, f"Tag '{tag}' not found in strip argument")

if __name__ == '__main__':
    unittest.main()
