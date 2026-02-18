"""Smoke tests for the CLI."""
import os
import subprocess
from pathlib import Path


def run(cmd):
    """Run a shell command with the repo source in PYTHONPATH."""
    env = os.environ.copy()
    repo_src = Path(__file__).resolve().parents[1] / 'src'
    env['PYTHONPATH'] = str(repo_src) + os.pathsep + env.get('PYTHONPATH', '')
    return subprocess.run(
        cmd, capture_output=True, text=True, shell=True, env=env, check=False
    )


def test_help_runs():
    """Test that the help command runs successfully."""
    r = run("python -m html2md --help")
    assert r.returncode == 0, r.stderr
