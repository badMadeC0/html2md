"""Tests for the Claude Code sensitive-file protection hook."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union

import pytest


HOOK_SCRIPT = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"


def run_hook(payload: Union[Dict[str, object], str]) -> subprocess.CompletedProcess:
    """Run the hook with a JSON payload or raw stdin text."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def tool_payload(tool_name: str, path: str) -> Dict[str, object]:
    """Build a minimal Claude Code hook payload."""
    return {"tool_name": tool_name, "tool_input": {"file_path": path}}


def test_blocks_sensitive_paths_case_insensitively() -> None:
    """Sensitive basenames are blocked regardless of case."""
    result = run_hook(tool_payload("Write", "config/PROD.PEM"))

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "config/PROD.PEM" in result.stderr


def test_blocks_notebook_path_field() -> None:
    """NotebookEdit payloads are inspected via notebook_path."""
    result = run_hook(
        {"tool_name": "NotebookEdit", "tool_input": {"notebook_path": "notes/.env.local"}}
    )

    assert result.returncode == 2
    assert "NotebookEdit" in result.stderr


def test_allows_non_edit_tools_for_sensitive_paths() -> None:
    """The hook only applies to tools that can modify files."""
    result = run_hook(tool_payload("Read", ".env"))

    assert result.returncode == 0
    assert result.stderr == ""


def test_allows_safe_edit_paths() -> None:
    """Non-sensitive edit paths are allowed."""
    result = run_hook(tool_payload("Edit", "src/html2md/cli.py"))

    assert result.returncode == 0
    assert result.stderr == ""


def test_malformed_payload_does_not_block() -> None:
    """Malformed JSON is reported without breaking agent execution."""
    result = run_hook("not json")

    assert result.returncode == 0
    assert "bad JSON payload" in result.stderr


def test_node_launcher_blocks_sensitive_file_without_pyenv_version() -> None:
    """The configured launcher should still block when pyenv cannot resolve bare python."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is required to exercise the Claude Code hook launcher")

    launcher_path = (
        Path(__file__).resolve().parents[1]
        / ".claude"
        / "hooks"
        / "run_protect_sensitive_files.js"
    )
    env = os.environ.copy()
    env.pop("PYENV_VERSION", None)
    result = subprocess.run(
        [node, str(launcher_path)],
        input=json.dumps(tool_payload("Write", ".env")),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_node_launcher_fails_closed_when_no_python_launcher(tmp_path: Path) -> None:
    """The launcher should block protected tools when Python cannot start."""
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is required to exercise the Claude Code hook launcher")

    launcher_path = (
        Path(__file__).resolve().parents[1]
        / ".claude"
        / "hooks"
        / "run_protect_sensitive_files.js"
    )
    env = os.environ.copy()
    env["PATH"] = str(tmp_path)
    result = subprocess.run(
        [node, str(launcher_path)],
        input=json.dumps(tool_payload("Write", ".env")),
        text=True,
        capture_output=True,
        check=False,
        env=env,
    )

    assert result.returncode == 2
    assert "no working Python 3 launcher found" in result.stderr


def test_hook_settings_uses_node_launcher_and_project_dir() -> None:
    """Claude Code should use the Node launcher from the project root."""
    settings_path = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    assert command == 'node "$CLAUDE_PROJECT_DIR/.claude/hooks/run_protect_sensitive_files.js"'
    assert "python" not in command


def test_node_launcher_prefers_python3_before_bare_python() -> None:
    """The launcher should avoid pyenv-sensitive bare python when python3 is available."""
    launcher_path = (
        Path(__file__).resolve().parents[1]
        / ".claude"
        / "hooks"
        / "run_protect_sensitive_files.js"
    )
    launcher = launcher_path.read_text(encoding="utf-8")

    python3_index = launcher.index('command: "python3"')
    py_index = launcher.index('command: "py"')
    python_index = launcher.index('command: "python"')

    assert python3_index < py_index < python_index
