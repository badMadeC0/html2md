import sys
import subprocess
import os
import pytest

def run(cmd):
    """Run a shell command."""
    env = os.environ.copy()
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    return subprocess.run(
        cmd, capture_output=True, text=True, shell=True, check=False, env=env
    )

def test_http_blocked():
    """Verify that http:// is blocked."""
    r = run(f"{sys.executable} -m html2md --url http://example.com")
    assert "Error: Invalid URL scheme" in r.stdout

def test_file_allowed():
    """Verify that file:// is allowed."""
    r = run(f"{sys.executable} -m html2md --url file:///etc/passwd")
    assert "Error: Invalid URL scheme" not in r.stdout
    # We expect it to try processing, even if it fails later
    assert "Processing URL: file:///etc/passwd" in r.stdout

def test_https_allowed():
    """Verify that https:// is allowed."""
    r = run(f"{sys.executable} -m html2md --url https://example.com")
    assert "Error: Invalid URL scheme" not in r.stdout
    assert "Processing URL: https://example.com" in r.stdout
