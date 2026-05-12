"""Tests for the Claude Code sensitive-file protection hook."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Union


HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"


def run_hook(payload: Union[Dict[str, object], str]) -> subprocess.CompletedProcess[str]:
    """Run the sensitive-file hook with a JSON payload."""
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=data,
        capture_output=True,
        text=True,
        check=False,
    )


def hook_payload(tool_name: str, path: str, key: str = "file_path") -> Dict[str, object]:
    """Build a minimal Claude Code hook payload."""
    return {"tool_name": tool_name, "tool_input": {key: path}}


def test_blocks_sensitive_edit_paths() -> None:
    """Sensitive paths are rejected for protected editing tools."""
    result = run_hook(hook_payload("Write", "config/.env.production"))

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "config/.env.production" in result.stderr


def test_blocks_sensitive_notebook_paths() -> None:
    """NotebookEdit payloads are checked with their notebook_path field."""
    result = run_hook(hook_payload("NotebookEdit", "notebooks/id_rsa", "notebook_path"))

    assert result.returncode == 2
    assert "notebooks/id_rsa" in result.stderr


def test_blocks_all_dotenv_variants() -> None:
    """Dotenv variants such as .envrc and .env-local are rejected."""
    for path in (".envrc", "config/.env-local"):
        result = run_hook(hook_payload("Write", path))

        assert result.returncode == 2
        assert path in result.stderr


def test_blocks_windows_separator_paths() -> None:
    """Backslash-separated paths are normalized before matching."""
    result = run_hook(hook_payload("Write", r"C:\repo\credentials.json"))

    assert result.returncode == 2
    assert "credentials.json" in result.stderr


def test_blocks_sensitive_multiedit_paths() -> None:
    """Nested MultiEdit edit targets are rejected."""
    result = run_hook(
        {
            "tool_name": "MultiEdit",
            "tool_input": {
                "edits": [
                    {"file_path": "src/html2md/cli.py", "old_string": "a", "new_string": "b"},
                    {"file_path": "secrets/id_rsa_backup", "old_string": "a", "new_string": "b"},
                ]
            },
        }
    )

    assert result.returncode == 2
    assert "id_rsa_backup" in result.stderr


def test_blocks_sensitive_symlink_name_before_realpath(tmp_path: Path) -> None:
    """Sensitive requested symlink names are checked before realpath resolution."""
    target = tmp_path / "non_sensitive_target"
    target.write_text("safe", encoding="utf-8")
    sensitive_link = tmp_path / ".env"
    sensitive_link.symlink_to(target)

    result = run_hook(hook_payload("Write", str(sensitive_link)))

    assert result.returncode == 2
    assert str(sensitive_link) in result.stderr


def test_allows_non_sensitive_edit_paths() -> None:
    """Non-sensitive paths are allowed for protected editing tools."""
    result = run_hook(hook_payload("Edit", "src/html2md/cli.py"))

    assert result.returncode == 0
    assert result.stderr == ""


def test_ignores_unprotected_tools() -> None:
    """Sensitive paths are only enforced for write-capable tools."""
    result = run_hook(hook_payload("Read", ".env"))

    assert result.returncode == 0
    assert result.stderr == ""


def test_malformed_payload_fails_open_with_diagnostic() -> None:
    """Malformed JSON does not break Claude Code hook processing."""
    result = run_hook("{")

    assert result.returncode == 0
    assert "bad JSON payload" in result.stderr
