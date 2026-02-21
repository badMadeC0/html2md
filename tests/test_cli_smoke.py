"""Smoke tests for CLI."""

import subprocess
import sys
import os


def run(cmd):
    """Run a shell command."""
    env = os.environ.copy()
    # Ensure src is in PYTHONPATH if not already set or installed
    src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
    if "PYTHONPATH" in env:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{env['PYTHONPATH']}"
    else:
        env["PYTHONPATH"] = src_path

    return subprocess.run(
        cmd, capture_output=True, text=True, shell=True, check=False, env=env
    )


def test_help_runs():
    """Test that help command runs successfully."""
    # Use python -m to run the module, which works without package installation
    r = run(f"{sys.executable} -m html2md --help")
    assert r.returncode == 0, r.stderr
