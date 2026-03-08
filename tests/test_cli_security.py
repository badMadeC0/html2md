"""Security tests for CLI."""

from io import StringIO
from unittest.mock import patch, MagicMock

from html2md.cli import main


def test_exception_output_sanitization():
    """Test that terminal control characters in exceptions are sanitized."""
    # Since requests is imported lazily inside `main`, we need to mock it in sys.modules
    # or patch the specific variable inside html2md.cli (but it's imported as a local variable).
    # The easiest way is to mock sys.modules for requests and markdownify.

    mock_requests = MagicMock()
    mock_session = MagicMock()
    mock_requests.Session.return_value = mock_session

    # Exception message with ANSI escape sequence (ESC) and Bell (BEL)
    vuln_msg = "Error: \x1b[31mRed Text\x1b[0m and \x07 bell\n\t."
    mock_session.get.side_effect = Exception(vuln_msg)

    mock_markdownify = MagicMock()

    with patch.dict(
        "sys.modules", {"requests": mock_requests, "markdownify": mock_markdownify}
    ):
        with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            main(["--url", "http://example.com"])

            output = mock_stdout.getvalue()

            assert "\x1b" not in output, "Output should not contain ESC characters"
            assert "\x07" not in output, "Output should not contain BEL characters"
            assert (
                "Error: [31mRed Text[0m and  bell\n\t." in output
            ), "Sanitized output should be printed"
