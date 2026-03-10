"""Security tests for SSRF/LFI protection."""

import io
import sys
from unittest.mock import patch

from html2md.cli import is_safe_url, main


def test_is_safe_url():
    """Test URL validation rules for SSRF protection."""
    # Safe URLs
    assert is_safe_url("http://example.com") is True
    assert is_safe_url("https://www.google.com/search?q=test") is True
    assert is_safe_url("https://8.8.8.8/dns") is True

    # Blocked schemes
    assert is_safe_url("file:///etc/passwd") is False
    assert is_safe_url("ftp://example.com") is False
    assert is_safe_url("gopher://example.com") is False
    assert is_safe_url("dict://example.com") is False

    # Blocked hostnames
    assert is_safe_url("http://localhost") is False
    assert is_safe_url("http://localhost:8080") is False
    assert is_safe_url("https://localhost.localdomain") is False
    assert is_safe_url("http://0.0.0.0") is False

    # Blocked IPs
    assert is_safe_url("http://127.0.0.1") is False # Loopback
    assert is_safe_url("http://169.254.169.254/latest/meta-data") is False # Link-local (AWS metadata)
    assert is_safe_url("http://10.0.0.1") is False # Private
    assert is_safe_url("http://192.168.1.1") is False # Private
    assert is_safe_url("http://172.16.0.1") is False # Private
    assert is_safe_url("http://224.0.0.1") is False # Multicast

    # Invalid URLs
    assert is_safe_url("not_a_url") is False
    assert is_safe_url("http://") is False


def test_cli_blocks_unsafe_urls():
    """Test that the CLI blocks unsafe URLs without fetching them."""
    unsafe_urls = [
        "file:///etc/passwd",
        "http://localhost:8080/admin",
        "http://169.254.169.254/latest/meta-data/",
    ]

    for url in unsafe_urls:
        captured_stderr = io.StringIO()
        with patch('sys.stderr', captured_stderr):
            # We don't need to mock requests because it should be blocked before fetching
            result = main(['--url', url])

            output = captured_stderr.getvalue()
            assert "is not safe to fetch" in output
            assert "SSRF/LFI protection" in output

            # CLI returns 0 on successful execution (even if URL processing fails gracefully)
            assert result == 0 or result is None
