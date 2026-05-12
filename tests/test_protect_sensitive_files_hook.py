"""Tests for the Claude Code sensitive-file protection hook."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional, Union


REPO_ROOT = Path(__file__).resolve().parents[1]
HOOK_SCRIPT = REPO_ROOT / ".claude" / "hooks" / "protect_sensitive_files.py"
HOOK_LAUNCHER = REPO_ROOT / ".claude" / "hooks" / "run_protect_sensitive_files.sh"
SETTINGS_PATH = REPO_ROOT / ".claude" / "settings.json"


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


def run_launcher(
    payload: Union[Dict[str, object], str], path: Optional[str] = None
) -> subprocess.CompletedProcess:
    """Run the hook launcher with a JSON payload or raw stdin text."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    env = os.environ.copy()
    if path is not None:
        env["PATH"] = path
    return subprocess.run(
        [str(HOOK_LAUNCHER)],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
        env=env,
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


def test_hook_launcher_preserves_blocking_exit() -> None:
    """The launcher must not fall through after the hook returns the blocking status."""
    result = run_launcher(tool_payload("Write", ".env"))

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr


def test_hook_settings_uses_shell_launcher_without_node_or_direct_python() -> None:
    """Claude Code should run the shell launcher instead of Node or a direct Python shim."""
    settings = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    assert command == '"$CLAUDE_PROJECT_DIR/.claude/hooks/run_protect_sensitive_files.sh"'
    assert "node" not in command
    assert "run_protect_sensitive_files.js" not in command
    assert "python" not in command


def test_hook_launcher_fails_closed_when_no_python_launcher_works(tmp_path: Path) -> None:
    """The shell fallback must return 2 if no Python command works."""
    for utility in ("cat", "dirname", "mktemp", "rm"):
        utility_path = Path(f"/usr/bin/{utility}")
        if not utility_path.exists():
            utility_path = Path(f"/bin/{utility}")
        (tmp_path / utility).symlink_to(utility_path)

    result = run_launcher(tool_payload("Write", ".env"), path=str(tmp_path))

    assert result.returncode == 2
    assert "no working Python 3 launcher found" in result.stderr


def test_hook_launcher_tries_python3_before_other_launchers() -> None:
    """The shell launcher should prefer python3 before py or python."""
    launcher = HOOK_LAUNCHER.read_text(encoding="utf-8")

    launcher_lines = [
        line for line in launcher.splitlines() if line.startswith("run_launcher ")
    ]

    assert launcher_lines == [
        "run_launcher python3",
        "run_launcher py -3",
        "run_launcher python",
    ]
