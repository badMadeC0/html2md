"""Test error handling in CLI."""
import sys
from unittest.mock import MagicMock, patch

def test_process_url_exception(capsys):
    """Test that exceptions during URL processing are caught and logged."""
    # Create mocks for dependencies
    mock_requests = MagicMock()
    mock_md = MagicMock()

    # Setup the exception to be raised by requests.Session().get()
    # Note: src/html2md/cli.py uses 'session = requests.Session()' and then 'session.get()'
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session
    mock_session.get.side_effect = Exception("Simulated Network Error")

    # Configure markdownify mock
    # The code does: from markdownify import markdownify as md
    # So the mock module needs a 'markdownify' attribute
    mock_md.markdownify = MagicMock()

    # Patch sys.modules to inject our mocks
    # We must patch sys.modules because 'requests' and 'markdownify' are imported
    # locally inside the 'main' function. Patching 'html2md.cli.requests' would fail
    # because 'requests' is not a module-level attribute of 'html2md.cli'.
    with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_md}):
        from html2md import cli

        # Run the CLI with a URL argument
        # The main function returns 0 on success/handled error, or 1 on critical failure
        exit_code = cli.main(['--url', 'http://example.com'])

        # Verify exit code (should be 0 because the exception is caught and printed)
        assert exit_code == 0

        # Verify that our mock was actually used
        mock_session.get.assert_called_once()

    # Capture stdout and stderr
    captured = capsys.readouterr()

    # Verify the error message is printed
    assert "Processing URL: http://example.com" in captured.out
    assert "Conversion failed: Simulated Network Error" in captured.out
