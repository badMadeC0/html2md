import unittest
from unittest.mock import patch, MagicMock
from html2md.cli import load_dependencies, setup_session, DependencyError

class TestCliRefactoring(unittest.TestCase):
    def test_load_dependencies_success(self):
        """Test loading dependencies works when available."""
        requests_module, md_func = load_dependencies()
        self.assertIsNotNone(requests_module)
        self.assertIsNotNone(md_func)
        self.assertTrue(callable(md_func))

    @patch('builtins.__import__')
    def test_load_dependencies_failure(self, mock_import):
        """Test load_dependencies raises DependencyError on failure."""
        mock_import.side_effect = ImportError("mock error")
        with self.assertRaises(DependencyError):
            load_dependencies()

    def test_setup_session(self):
        """Test setup_session configures default headers correctly."""
        mock_requests = MagicMock()
        mock_session_obj = MagicMock()
        mock_requests.Session.return_value = mock_session_obj
        mock_session_obj.headers = {}

        session = setup_session(mock_requests)

        self.assertEqual(session, mock_session_obj)
        self.assertIn('User-Agent', session.headers)
        self.assertIn('Accept', session.headers)

if __name__ == '__main__':
    unittest.main()
