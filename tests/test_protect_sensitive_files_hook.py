from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, Dict


PROJECT_ROOT = Path(__file__).resolve().parents[1]
HOOK = PROJECT_ROOT / ".claude" / "hooks" / "protect_sensitive_files.py"

spec = importlib.util.spec_from_file_location("protect_sensitive_files", str(HOOK))
assert spec is not None
assert spec.loader is not None
protect_sensitive_files = importlib.util.module_from_spec(spec)
spec.loader.exec_module(protect_sensitive_files)
SENSITIVE_BASENAME_PATTERNS = protect_sensitive_files.SENSITIVE_BASENAME_PATTERNS


def run_hook(payload: Dict[str, Any]) -> subprocess.CompletedProcess:
    return run_hook_raw(json.dumps(payload))


def run_hook_raw(payload: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )


def find_pattern(predicate: Callable[[str], bool], description: str) -> str:
    for pattern in SENSITIVE_BASENAME_PATTERNS:
        if predicate(pattern):
            return pattern
    raise AssertionError(f"missing expected sensitive pattern: {description}")


def test_blocks_sensitive_file_path() -> None:
    env_pattern = find_pattern(lambda pattern: pattern.startswith(".env."), ".env.*")
    sensitive_env = env_pattern.replace("*", "production")
    result = run_hook(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "config/" + sensitive_env},
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert sensitive_env in result.stderr


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
    env_basename = find_pattern(lambda pattern: pattern == ".env", ".env")
    result = run_hook(
        {
            "tool_name": "Read",
            "tool_input": {"file_path": env_basename},
        }
    )

    assert result.returncode == 0
    assert result.stderr == ""


def test_blocks_common_ssh_key_basenames() -> None:
    expected_private = {"id_ed25519", "id_ecdsa", "id_dsa"}
    expected_public = {f"{basename}.pub" for basename in expected_private}
    patterns = set(SENSITIVE_BASENAME_PATTERNS)

    for basename in expected_private | expected_public:
        assert basename in patterns

    for basename in sorted(expected_private | expected_public):
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


def test_blocks_nested_multi_edit_sensitive_file_path() -> None:
    ssh_private_key = find_pattern(
        lambda pattern: pattern.startswith("id_ed") and not pattern.endswith(".pub"),
        "id_ed private key",
    )

    result = run_hook(
        {
            "tool_name": "MultiEdit",
            "tool_input": {
                "edits": [
                    {
                        "file_path": "src/html2md/cli.py",
                        "old_string": "a",
                        "new_string": "b",
                    },
                    {
                        "metadata": {
                            "file_path": ".ssh/" + ssh_private_key,
                        },
                        "old_string": "old",
                        "new_string": "new",
                    },
                ],
            },
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert ssh_private_key in result.stderr


def test_blocks_notebook_edit_sensitive_notebook_path() -> None:
    certificate_pattern = find_pattern(lambda pattern: pattern == "*.crt", "*.crt")
    sensitive_certificate = certificate_pattern.replace("*", "client")
    result = run_hook(
        {
            "tool_name": "NotebookEdit",
            "tool_input": {"notebook_path": "notebooks/" + sensitive_certificate},
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert sensitive_certificate in result.stderr


def test_bad_json_payload_fails_closed() -> None:
    result = run_hook_raw("{")

    assert result.returncode == 1
    assert "bad JSON payload" in result.stderr


def test_empty_payload_fails_closed() -> None:
    result = run_hook_raw("")

    assert result.returncode == 1
    assert "empty hook payload" in result.stderr


def test_non_object_json_payload_fails_closed() -> None:
    result = run_hook_raw("[]")

    assert result.returncode == 1
    assert "hook payload must be a JSON object" in result.stderr
