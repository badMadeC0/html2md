"""Security tests for CLI filename generation."""

from html2md.cli import _secure_filename

def test_secure_filename_basic():
    """Test basic filename generation."""
    assert _secure_filename("normal") == "normal"
    assert _secure_filename("foo.html") == "foo.html"
    assert _secure_filename("index") == "index"

def test_secure_filename_path_traversal():
    """Test that path traversal attempts are neutralized."""
    assert _secure_filename("../../etc/passwd") == "etc_passwd"
    assert _secure_filename("..\\..\\Windows\\System32\\cmd.exe") == "Windows_System32_cmd.exe"
    assert _secure_filename("../../../../../foo/bar") == "foo_bar"

def test_secure_filename_url_encoded():
    """Test that URL-encoded path traversals are neutralized."""
    assert _secure_filename("..%2f..%2f..%2fetc%2fpasswd") == "etc_passwd"
    assert _secure_filename("%2e%2e%2f%2e%2e%2fetc%2fpasswd") == "etc_passwd"
    assert _secure_filename("%2e%2e\\%2e%2e\\Windows") == "Windows"

def test_secure_filename_null_bytes():
    """Test that null bytes are removed/replaced."""
    assert _secure_filename("foo%00bar") == "foo_bar"
    assert _secure_filename("foo\0bar") == "foo_bar"

def test_secure_filename_empty_or_dangerous_only():
    """Test behavior when filename becomes empty or consists only of dangerous chars."""
    assert _secure_filename("") == "conversion_result"
    assert _secure_filename("/") == "conversion_result"
    assert _secure_filename("../..") == "conversion_result"
    assert _secure_filename("..%2f..") == "conversion_result"

def test_secure_filename_multiple_separators():
    """Test that multiple separators are collapsed."""
    assert _secure_filename("foo///bar") == "foo_bar"
    assert _secure_filename("foo%2f%2f%2fbar") == "foo_bar"
