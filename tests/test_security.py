
import pytest
from unittest.mock import MagicMock, patch
import html2md.cli

def test_xss_sanitization(capsys):
    """Test that malicious HTML is sanitized before conversion to Markdown."""

    # Mock malicious HTML content
    malicious_html = """
    <html>
        <body>
            <a href="javascript:alert('xss')">Click me</a>
            <img src="valid.png" onerror="alert('xss')">
            <p onclick="alert('xss')">Click me too</p>
            <a href="http://example.com">Safe link</a>
        </body>
    </html>
    """

    # Setup mock for requests.Session
    mock_response = MagicMock()
    mock_response.text = malicious_html
    mock_response.raise_for_status = MagicMock()

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    # Ensure we use the real markdownify library for accurate test results
    import markdownify
    real_md = markdownify.markdownify

    with patch('requests.Session', return_value=mock_session):
        # We need to ensure the CLI uses the real markdownify.
        # Since it imports 'markdownify' inside the function, patching it here
        # is tricky if we don't control the import mechanism.
        # However, simply running the function in an environment where markdownify is installed
        # (which it is) should be sufficient.

        # Call the CLI main function
        html2md.cli.main(['--url', 'http://example.com'])

        captured = capsys.readouterr()
        output = captured.out

        # Assertions
        assert "[Click me](javascript:alert('xss'))" not in output, "Javascript link was not removed"
        assert "onerror" not in output, "onerror attribute was not removed"
        assert "onclick" not in output, "onclick attribute was not removed"
        assert "[Safe link](http://example.com)" in output, "Safe link was incorrectly removed"
