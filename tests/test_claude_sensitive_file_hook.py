from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "protect_sensitive_files.py"
)


def run_hook(payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def test_configured_hook_command_uses_project_root_from_subdirectory() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    settings_path = repo_root / ".claude" / "settings.json"
    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]

    assert command.startswith('python -c "')
    assert "$CLAUDE_PROJECT_DIR" not in command
    assert "%CLAUDE_PROJECT_DIR%" not in command
    assert "os.environ['CLAUDE_PROJECT_DIR']" in command

    result = subprocess.run(
        command,
        input=json.dumps({"tool_input": {"file_path": ".env"}}),
        text=True,
        capture_output=True,
        check=False,
        cwd=repo_root / "src",
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(repo_root)},
        shell=True,
    )

    assert result.returncode == 2
    assert "Blocked edit to sensitive file path" in result.stderr


def test_hook_blocks_env_file_edits() -> None:
    result = run_hook({"tool_input": {"file_path": ".env"}})

    assert result.returncode == 2
    assert "Blocked edit to sensitive file path" in result.stderr


def test_hook_blocks_nested_multi_edit_secret_paths() -> None:
    result = run_hook(
        {
            "tool_input": {
                "edits": [
                    {"file_path": "src/html2md/cli.py"},
                    {"file_path": "config/private.pem"},
                ]
            }
        }
    )

    assert result.returncode == 2
    assert "config/private.pem" in result.stderr


def test_hook_allows_regular_source_files() -> None:
    result = run_hook({"tool_input": {"file_path": "src/html2md/cli.py"}})

    assert result.returncode == 0
    assert result.stderr == ""
