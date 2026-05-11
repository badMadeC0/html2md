"""Tests for the Claude sensitive-file protection hook."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch


HOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "protect-sensitive-files.py"
)


def load_hook_module():
    """Load the hook script as a module for direct helper tests."""
    spec = importlib.util.spec_from_file_location("protect_sensitive_files", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_hook(payload: dict[str, object]) -> subprocess.CompletedProcess[str]:
    """Run the hook with a serialized Claude Code payload."""
    return run_hook_raw(json.dumps(payload))


def run_hook_raw(payload: str) -> subprocess.CompletedProcess[str]:
    """Run the hook with raw stdin content."""
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload,
        text=True,
        capture_output=True,
        check=False,
    )


def test_is_sensitive_matches_secret_basenames():
    """Sensitive basename patterns are blocked at any path depth."""
    hook = load_hook_module()

    assert hook.is_sensitive(".env")
    assert hook.is_sensitive("config/.env.local")
    assert hook.is_sensitive("keys/service-account.pem")
    assert hook.is_sensitive("nested/credentials.json")
    assert hook.is_sensitive(".ssh/id_ed25519")
    assert hook.is_sensitive(".ssh/id_ecdsa")
    assert hook.is_sensitive(".ssh/id_dsa")
    assert not hook.is_sensitive("docs/env-example.md")


def test_is_sensitive_checks_raw_symlink_filename(tmp_path):
    """A sensitive symlink name is blocked even when its target basename is safe."""
    hook = load_hook_module()
    safe_target = tmp_path / "safe-target.txt"
    sensitive_link = tmp_path / ".env"
    safe_target.write_text("not secret", encoding="utf-8")
    sensitive_link.symlink_to(safe_target)

    assert hook.is_sensitive(str(sensitive_link))


def test_is_sensitive_checks_resolved_symlink_target(tmp_path):
    """A safe-looking symlink name is blocked when it resolves to a sensitive file."""
    hook = load_hook_module()
    sensitive_target = tmp_path / "id_ed25519"
    safe_link = tmp_path / "safe-target.txt"
    sensitive_target.write_text("secret", encoding="utf-8")
    safe_link.symlink_to(sensitive_target)

    assert hook.is_sensitive(str(safe_link))


def test_candidate_paths_extracts_supported_keys_only():
    """Only supported Claude Code path keys are considered targets."""
    hook = load_hook_module()

    assert hook.candidate_paths(
        {
            "file_path": "src/app.py",
            "path": "README.md",
            "notebook_path": "notes.ipynb",
            "url": "https://example.com/.env",
            "empty": "",
            "edits": [
                {"file_path": "src/one.py"},
                {"path": "src/two.py"},
                {"notebook_path": "notes/two.ipynb"},
                {"url": "https://example.com/secret.key"},
                "not-a-dict",
            ],
        }
    ) == [
        "src/app.py",
        "README.md",
        "notes.ipynb",
        "src/one.py",
        "src/two.py",
        "notes/two.ipynb",
    ]


def test_hook_blocks_protected_tool_targeting_sensitive_file():
    """Protected tools fail closed when the target is a sensitive file."""
    result = run_hook(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "secrets/.env.production"},
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "secrets/.env.production" in result.stderr


def test_hook_allows_unprotected_tool_targeting_sensitive_file():
    """Read-only or unrelated tools are not blocked by this hook."""
    result = run_hook(
        {
            "tool_name": "Read",
            "tool_input": {"file_path": "secrets/.env.production"},
        }
    )

    assert result.returncode == 0
    assert result.stderr == ""


def test_hook_allows_protected_tool_targeting_regular_file():
    """Protected tools can continue when targets are not sensitive."""
    result = run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/html2md/cli.py"},
        }
    )

    assert result.returncode == 0
    assert result.stderr == ""


def test_hook_blocks_multiedit_nested_sensitive_file():
    """Nested MultiEdit targets are inspected before allowing the tool."""
    result = run_hook(
        {
            "tool_name": "MultiEdit",
            "tool_input": {
                "edits": [
                    {"file_path": "src/html2md/cli.py"},
                    {"file_path": ".ssh/id_ed25519"},
                ],
            },
        }
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert ".ssh/id_ed25519" in result.stderr


def test_hook_fails_closed_on_bad_json():
    """Malformed non-empty payloads are rejected because safety cannot be verified."""
    result = run_hook_raw("{not valid json")

    assert result.returncode == 1
    assert "bad JSON payload" in result.stderr


def test_hook_fails_closed_when_stdin_read_fails(capsys):
    """stdin read failures are rejected because safety cannot be verified."""
    hook = load_hook_module()

    with patch.object(hook.sys.stdin, "read", side_effect=OSError("boom")):
        assert hook.main() == 1

    assert "failed to read stdin" in capsys.readouterr().err
