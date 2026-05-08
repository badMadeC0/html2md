"""Smoke tests for CLI."""

import os
import subprocess
import sys

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
    # Use python -m html2md to ensure tests pass even if package is not installed globally
    r = run(f"{sys.executable} -m html2md --help")
    assert r.returncode == 0, r.stderr


def test_gui_flags_are_accepted(capsys, monkeypatch):
    """GUI-restored flags should be valid for the console entry point."""
    from html2md import cli

    class DummyResponse:
        text = "<html><body><main><h1>Hello</h1></main></body></html>"

        def raise_for_status(self):
            return None

    monkeypatch.setattr("requests.Session.get", lambda *args, **kwargs: DummyResponse())
    result = cli.main([
        "--url",
        "http://example.com/page",
        "--all-formats",
        "--main-content",
    ])
    outerr = capsys.readouterr()

    assert result == 0
    assert "unrecognized arguments" not in outerr.err
    assert "# Hello" in outerr.out
