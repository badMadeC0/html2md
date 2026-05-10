"""Tests for the Claude Code sensitive-file protection hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union


HOOK_SCRIPT = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"


def run_hook(payload: Union[Dict[str, object], str]) -> subprocess.CompletedProcess[str]:
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


def test_hook_settings_uses_python_directly_and_fails_closed() -> None:
    """Claude Code should run Python directly and block if launch fails."""
    settings_path = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    assert command == (
        'python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/protect_sensitive_files.py" '
        '|| py -3 "$CLAUDE_PROJECT_DIR/.claude/hooks/protect_sensitive_files.py" '
        '|| python "$CLAUDE_PROJECT_DIR/.claude/hooks/protect_sensitive_files.py" '
        '|| exit 2'
    )
    assert "node" not in command
    assert "run_protect_sensitive_files.js" not in command
    assert command.endswith("|| exit 2")


def test_hook_settings_fails_closed_when_no_python_launcher_works(tmp_path: Path) -> None:
    """The configured shell fallback must return 2 if no Python command works."""
    settings_path = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    env = {
        "CLAUDE_PROJECT_DIR": str(Path(__file__).resolve().parents[1]),
        "PATH": str(tmp_path),
    }

    result = subprocess.run(
        command,
        input=json.dumps(tool_payload("Write", ".env")),
        text=True,
        capture_output=True,
        check=False,
        env=env,
        shell=True,
    )

    assert result.returncode == 2
