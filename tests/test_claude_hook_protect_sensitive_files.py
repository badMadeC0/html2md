"""Tests for the Claude Code sensitive-file protection hook."""
from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path
from types import ModuleType


HOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "protect-sensitive-files.py"
)


def _load_hook() -> ModuleType:
    """Load the hook script as a Python module for direct unit testing."""
    spec = importlib.util.spec_from_file_location("protect_sensitive_files", HOOK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_hook(payload: object, monkeypatch) -> int:
    """Run the hook with a JSON-serializable stdin payload."""
    hook = _load_hook()
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    return hook.main([])


def test_sensitive_basename_patterns_match_case_insensitively():
    """Sensitive basenames are detected regardless of path depth or casing."""
    hook = _load_hook()

    assert hook.is_sensitive(".env")
    assert hook.is_sensitive("CONFIG/.ENV.PROD")
    assert hook.is_sensitive("secrets/api.PEM")
    assert hook.is_sensitive("nested/credentials.json")
    assert hook.is_sensitive(r"C:\\repo\\secrets\\id_rsa")
    assert hook.is_sensitive("~/.ssh/id_ed25519")
    assert hook.is_sensitive("~/.ssh/id_ecdsa")
    assert hook.is_sensitive("~/.ssh/id_dsa")
    assert not hook.is_sensitive("docs/credentials-example.json")


def test_hook_blocks_protected_tool_targeting_sensitive_file(monkeypatch, capsys):
    """Protected edit tools return exit code 2 for sensitive target paths."""
    status = _run_hook(
        {
            "tool_name": "Write",
            "tool_input": {"file_path": "config/.env.local"},
        },
        monkeypatch,
    )

    assert status == 2
    assert "BLOCKED" in capsys.readouterr().err


def test_hook_allows_non_sensitive_file_for_protected_tool(monkeypatch):
    """Protected edit tools return zero for ordinary source files."""
    status = _run_hook(
        {
            "tool_name": "Edit",
            "tool_input": {"file_path": "src/html2md/cli.py"},
        },
        monkeypatch,
    )

    assert status == 0


def test_hook_allows_sensitive_file_for_unprotected_tool(monkeypatch):
    """Read-only or unrelated tools are ignored by the edit guard."""
    status = _run_hook(
        {
            "tool_name": "Read",
            "tool_input": {"file_path": ".env"},
        },
        monkeypatch,
    )

    assert status == 0


def test_hook_fails_open_for_malformed_json(monkeypatch, capsys):
    """Malformed hook payloads emit diagnostics but do not block execution."""
    hook = _load_hook()
    monkeypatch.setattr(sys, "stdin", io.StringIO("{"))

    assert hook.main([]) == 0
    assert "bad JSON payload" in capsys.readouterr().err
