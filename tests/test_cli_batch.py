import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

class TestCliBatch(unittest.TestCase):
    @patch('html2md.cli.process_url')
    @patch('os.path.exists')
    def test_batch_empty_lines_skipped(self, mock_exists, mock_process_url):
        """Test that empty lines and whitespace-only lines in batch file are skipped."""
        from html2md.cli import main

        # Mock dependencies modules to avoid ImportError
        mock_requests = MagicMock()
        mock_md = MagicMock()

        # Batch file content with valid URLs, empty lines, and whitespace lines
        batch_content = "http://example.com/valid1\n\n   \nhttp://example.com/valid2\n"

        mock_exists.side_effect = lambda p: True if p == 'urls.txt' else False

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_md}):
            with patch('builtins.open', mock_open(read_data=batch_content)):
                # Run the main function with --batch
                main(['--batch', 'urls.txt'])

        # Verify that process_url was only called for the non-empty lines
        self.assertEqual(mock_process_url.call_count, 2)

        # Check call arguments
        calls = mock_process_url.call_args_list
        self.assertEqual(calls[0][0][0], "http://example.com/valid1")
        self.assertEqual(calls[1][0][0], "http://example.com/valid2")

if __name__ == '__main__':
    unittest.main()
