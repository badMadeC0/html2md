"""Smoke tests for CLI."""

import subprocess
import sys

def run(cmd):
    """Run a shell command."""
    return subprocess.run(cmd, capture_output=True, text=True, shell=True, check=False)

def test_help_runs():
    """Test that help command runs successfully."""
    # Use python -m html2md to ensure tests pass even if package is not installed globally
    r = run(f"{sys.executable} -m html2md --help")
    assert r.returncode == 0, r.stderr
