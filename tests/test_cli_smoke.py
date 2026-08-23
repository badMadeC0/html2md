"""Smoke tests for CLI."""

import os
import subprocess
import sys

def run(cmd_list):
    """Run a shell command safely without shell=True."""
    env = os.environ.copy()
    # Ensure src is in PYTHONPATH if not already set or installed
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    # Security: shell=True is removed to prevent command injection.
    # Commands must be passed as a list of arguments.
    return subprocess.run(
        cmd_list, capture_output=True, text=True, check=False, env=env
    )


def test_help_runs():
    """Test that help command runs successfully."""
    # Use python -m html2md to ensure tests pass even if package is not installed globally
    r = run([sys.executable, "-m", "html2md", "--help"])
    assert r.returncode == 0, r.stderr
