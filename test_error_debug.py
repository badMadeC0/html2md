import unittest
from unittest.mock import patch, MagicMock
import sys
import io
import os
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import html2md.cli

class TestCliError(unittest.TestCase):
    def test_cli_conversion_request_failure(self):
        mock_requests = MagicMock()
        mock_requests.RequestException = requests.RequestException

        mock_session = MagicMock()
        mock_requests.Session.return_value = mock_session
        mock_session.get.side_effect = requests.RequestException("Network error")

        mock_markdownify = MagicMock()

        captured_stderr = io.StringIO()
        captured_stdout = io.StringIO()

        with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):
            with patch('sys.stderr', captured_stderr), patch('sys.stdout', captured_stdout):
                html2md.cli.main(['--url', 'http://example.com'])

        output = captured_stderr.getvalue()
        stdout_output = captured_stdout.getvalue()

        print("ERR:", repr(output))
        print("OUT:", repr(stdout_output))

if __name__ == '__main__':
    unittest.main()
