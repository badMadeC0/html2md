"""Tests for CLI security mitigations like path traversal."""

from html2md.cli import sanitize_filename


def test_sanitize_filename_normal():
    assert sanitize_filename("index.html") == "index.html"
    assert sanitize_filename("about-us") == "about-us"


def test_sanitize_filename_path_traversal():
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("..\\..\\Windows\\System32\\cmd.exe") == "cmd.exe"
    assert sanitize_filename("/absolute/path/to/file.txt") == "file.txt"
    assert sanitize_filename("C:\\absolute\\path\\to\\file.txt") == "file.txt"


def test_sanitize_filename_url_encoded():
    assert sanitize_filename("%2e%2e%2f%2e%2e%2fetc%2fpasswd") == "passwd"
    assert (
        sanitize_filename("%2e%2e%5c%2e%2e%5cWindows%5cSystem32%5ccmd.exe") == "cmd.exe"
    )


def test_sanitize_filename_mixed_encoding():
    assert sanitize_filename("..%2f..%2fetc/passwd") == "passwd"
    assert sanitize_filename("%2e%2e/etc/passwd") == "passwd"


def test_sanitize_filename_edge_cases():
    assert sanitize_filename(".") == "download"
    assert sanitize_filename("..") == "download"
    assert sanitize_filename("") == ""
    assert sanitize_filename("/") == "download"
    assert sanitize_filename("\\") == "download"
    assert sanitize_filename("///") == "download"
    assert sanitize_filename("%2f%2f%2f") == "download"


def test_sanitize_filename_strips_dots():
    assert sanitize_filename(".hidden") == "hidden"
    assert sanitize_filename("file.") == "file"
    assert sanitize_filename("...file...") == "file"
