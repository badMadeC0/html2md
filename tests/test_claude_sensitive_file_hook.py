from __future__ import annotations

import json
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
