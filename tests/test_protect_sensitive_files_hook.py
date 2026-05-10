from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


HOOK = Path(__file__).resolve().parents[1] / ".claude" / "hooks" / "protect_sensitive_files.py"
SPEC = importlib.util.spec_from_file_location("protect_sensitive_files", str(HOOK))
assert SPEC is not None
HOOK_MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(HOOK_MODULE)

EXPECTED_SENSITIVE_SSH_KEY_BASENAMES = (
    "id_ed25519",
    "id_ed25519.pub",
    "id_ed25519_sk",
    "id_ed25519_sk.pub",
    "id_ecdsa",
    "id_ecdsa.pub",
    "id_ecdsa_sk",
    "id_ecdsa_sk.pub",
    "id_dsa",
    "id_dsa.pub",
)


def run_hook(payload: Dict[str, Any]) -> subprocess.CompletedProcess:
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


def test_blocks_common_ssh_private_key_basenames() -> None:
    assert set(EXPECTED_SENSITIVE_SSH_KEY_BASENAMES).issubset(
        HOOK_MODULE.SENSITIVE_BASENAME_PATTERNS
    )

    for basename in EXPECTED_SENSITIVE_SSH_KEY_BASENAMES:
        target = f".ssh/{basename}"
        result = run_hook(
            {
                "tool_name": "Write",
                "tool_input": {"file_path": target},
            }
        )

        assert result.returncode == 2
        assert "BLOCKED" in result.stderr
        assert target in result.stderr
