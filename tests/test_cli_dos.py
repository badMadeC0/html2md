import sys
from unittest.mock import MagicMock, patch
import unittest
import io

# Pre-mock dependencies if missing (for restricted environments)
if 'requests' not in sys.modules:
    mock_requests = MagicMock()
    class MockRequestException(Exception): pass
    mock_requests.RequestException = MockRequestException
    sys.modules['requests'] = mock_requests
    sys.modules['markdownify'] = MagicMock()

# Import after mocking
from html2md.cli import main

class TestCliDoS(unittest.TestCase):
    def setUp(self):
        self.stderr = io.StringIO()
        self.stdout = io.StringIO()
        self.stderr_patch = patch('sys.stderr', self.stderr)
        self.stdout_patch = patch('sys.stdout', self.stdout)
        self.stderr_patch.start()
        self.stdout_patch.start()

    def tearDown(self):
        self.stderr_patch.stop()
        self.stdout_patch.stop()

    @patch('requests.Session')
    def test_large_content_length(self, mock_session_cls):
        """Test that requests with Content-Length > limit are rejected."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_response = MagicMock()
        # 15 MB, limit is 10 MB
        mock_response.headers = {'Content-Length': str(15 * 1024 * 1024)}
        mock_response.iter_content.return_value = [b'a']
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None

        mock_session.get.return_value = mock_response

        main(['--url', 'http://example.com/large'])

        output = self.stderr.getvalue()
        # The ValueError is caught by the generic Exception handler in process_url
        self.assertIn("Conversion failed", output)
        self.assertIn("Content too large", output)

    @patch('requests.Session')
    def test_large_stream_content(self, mock_session_cls):
        """Test that requests without Content-Length but large body are rejected."""
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        mock_response = MagicMock()
        mock_response.headers = {} # No Content-Length

        # Generate chunks that sum up to > 10MB
        chunks = [b'a' * 1024 * 1024] * 11
        mock_response.iter_content.return_value = chunks
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None

        mock_session.get.return_value = mock_response

        main(['--url', 'http://example.com/large_stream'])

        output = self.stderr.getvalue()
        self.assertIn("Conversion failed", output)
        self.assertIn("Content exceeded limit", output)

if __name__ == '__main__':
    unittest.main()
