from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"


def run_hook(payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def test_blocks_sensitive_file_path() -> None:
    result = run_hook(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "config/.env.production"},
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "config/.env.production" in result.stderr


def test_allows_non_sensitive_file_path() -> None:
    result = run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/html2md/cli.py"},
        }
    )

    assert result.returncode == 0
    assert result.stderr == ""


def test_ignores_unprotected_tool() -> None:
    result = run_hook(
        {
            "tool_name": "Read",
            "tool_input": {"file_path": ".env"},
        }
    )

    assert result.returncode == 0
    assert result.stderr == ""
