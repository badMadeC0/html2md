"""Tests for the Claude sensitive-file protection hook."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


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
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
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
    ssh_key_basenames = (
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
    for basename in ssh_key_basenames:
        assert basename in hook.SENSITIVE_BASENAME_PATTERNS
        assert hook.is_sensitive(f".ssh/{basename}")
    assert not hook.is_sensitive("docs/env-example.md")


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
        }
    ) == ["src/app.py", "README.md", "notes.ipynb"]


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
