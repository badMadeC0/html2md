"""Smoke tests for CLI."""

import subprocess

def run(cmd):
    """Run a shell command."""
    return subprocess.run(cmd, capture_output=True, text=True, shell=True, check=False)

def test_help_runs():
    """Test that help command runs successfully."""
    r = run("html2md --help")
    assert r.returncode == 0, r.stderr
