import subprocess
import logging


def test_logging_output():
    """Test that logs go to stderr and content output goes to stdout."""

    # Reset logging handlers in the current process; actual logging config
    # for the CLI will be exercised in the subprocess.
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Run the CLI as a module in a subprocess with a URL argument.
    result = subprocess.run(
        [sys.executable, "-m", "html2md", "--url", "http://example.com"],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0

    # Assert logs are in stderr
    assert "Processing URL: http://example.com" in result.stderr
    assert "Fetching content..." in result.stderr
    assert "Converting to Markdown..." in result.stderr

    # Assert content is in stdout
    assert "# Markdown Content" in result.stdout

    # Assert logs are NOT in stdout
    assert "Processing URL" not in result.stdout
