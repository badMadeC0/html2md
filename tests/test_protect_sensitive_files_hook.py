from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


HOOK_PATH = (
    Path(__file__).resolve().parents[1]
    / ".claude"
    / "hooks"
    / "protect-sensitive-files.py"
)


def load_hook_module():
    spec = importlib.util.spec_from_file_location("protect_sensitive_files", HOOK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_hook(payload, monkeypatch, capsys):
    module = load_hook_module()
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    exit_code = module.main([])
    captured = capsys.readouterr()
    return exit_code, captured


def test_blocks_write_to_env_file(monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": "Write", "tool_input": {"file_path": "config/.env"}},
        monkeypatch,
        capsys,
    )

    assert exit_code == 2
    assert "BLOCKED" in captured.err
    assert "config/.env" in captured.err


def test_blocks_notebook_edit_to_sensitive_notebook_path(monkeypatch, capsys):
    exit_code, captured = run_hook(
        {
            "tool_name": "NotebookEdit",
            "tool_input": {"notebook_path": "notebooks/private.key"},
        },
        monkeypatch,
        capsys,
    )

    assert exit_code == 2
    assert "private.key" in captured.err


@pytest.mark.parametrize(
    "ssh_key_path",
    [
        "~/.ssh/id_ed25519",
        "~/.ssh/id_ecdsa",
        "~/.ssh/id_dsa",
        "~/.ssh/id_rsa",
        "~/.ssh/id_ed25519.pub",
    ],
)
def test_blocks_common_openssh_key_basenames(ssh_key_path, monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": "Edit", "tool_input": {"file_path": ssh_key_path}},
        monkeypatch,
        capsys,
    )

    assert exit_code == 2
    assert "BLOCKED" in captured.err
    assert ssh_key_path in captured.err


def test_allows_unprotected_tool_targeting_sensitive_file(monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": "Read", "tool_input": {"file_path": ".env"}},
        monkeypatch,
        capsys,
    )

    assert exit_code == 0
    assert captured.err == ""


def test_allows_protected_tool_targeting_regular_file(monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": "Edit", "tool_input": {"file_path": "src/app.py"}},
        monkeypatch,
        capsys,
    )

    assert exit_code == 0
    assert captured.err == ""


def test_bad_json_allows_and_reports_error(monkeypatch, capsys):
    module = load_hook_module()
    monkeypatch.setattr(sys, "stdin", io.StringIO("{"))

    exit_code = module.main([])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "bad JSON payload" in captured.err


def test_claude_settings_registers_pre_tool_use_hook():
    settings_path = Path(__file__).resolve().parents[1] / ".claude" / "settings.json"

    settings = json.loads(settings_path.read_text(encoding="utf-8"))
    pre_tool_use = settings["hooks"]["PreToolUse"]

    protected_entry = next(
        entry
        for entry in pre_tool_use
        if entry.get("matcher") == "Edit|Write|MultiEdit|NotebookEdit"
    )
    commands = [
        hook
        for hook in protected_entry["hooks"]
        if hook.get("type") == "command"
    ]

    assert commands == [
        {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/protect-sensitive-files.py",
        }
    ]


def test_registered_hook_command_blocks_sensitive_file():
    repo_root = Path(__file__).resolve().parents[1]
    settings = json.loads(
        (repo_root / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": "secrets/.env"}}
    )

    result = subprocess.run(
        command,
        input=payload,
        text=True,
        capture_output=True,
        shell=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(repo_root)},
        check=False,
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "secrets/.env" in result.stderr
