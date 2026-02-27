"""Security validation tests for CLI."""

import os
import subprocess
import sys

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

def test_invalid_scheme_url():
    """Test that non-http/https URLs are rejected."""
    # Using 'ftp' scheme which should be rejected
    cmd = f"{sys.executable} -m html2md --url ftp://example.com"
    r = run(cmd)

    # It should fail
    assert r.returncode != 0, f"Expected non-zero return code, got {r.returncode}"

    # It should print a specific error message about the scheme
    if "Error: Invalid URL scheme" not in r.stdout and "Error: Invalid URL scheme" not in r.stderr:
         assert False, f"Expected error message 'Error: Invalid URL scheme' not found. Output: {r.stdout} {r.stderr}"
