"""Tests for the Claude Code sensitive-file protection hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HOOK_SCRIPT = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"


def run_hook(payload: dict[str, object] | str) -> subprocess.CompletedProcess[str]:
    """Run the hook with a JSON payload or raw stdin text."""
    stdin = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK_SCRIPT)],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def tool_payload(tool_name: str, path: str) -> dict[str, object]:
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
