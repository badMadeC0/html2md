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


def run_hook_raw(payload_raw, monkeypatch, capsys):
    module = load_hook_module()
    monkeypatch.setattr(sys, "stdin", io.StringIO(payload_raw))
    exit_code = module.main([])
    captured = capsys.readouterr()
    return exit_code, captured


def run_hook(payload, monkeypatch, capsys):
    return run_hook_raw(json.dumps(payload), monkeypatch, capsys)


@pytest.mark.parametrize(
    ("tool_name", "tool_input", "expected_path"),
    [
        ("Write", {"file_path": "config/.env"}, "config/.env"),
        (
            "NotebookEdit",
            {"notebook_path": "notebooks/private.key"},
            "notebooks/private.key",
        ),
        (
            "MultiEdit",
            {
                "edits": [
                    {"file_path": "src/app.py", "old_string": "a", "new_string": "b"},
                    {
                        "file_path": "keys/id_ed25519",
                        "old_string": "x",
                        "new_string": "y",
                    },
                ]
            },
            "keys/id_ed25519",
        ),
    ],
)
def test_blocks_sensitive_files(tool_name, tool_input, expected_path, monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": tool_name, "tool_input": tool_input},
        monkeypatch,
        capsys,
    )

    assert exit_code == 2
    assert "BLOCKED" in captured.err
    assert expected_path in captured.err


@pytest.mark.parametrize(
    "file_path",
    [
        "keys/id_rsa",
        "keys/id_rsa.pub",
        "keys/id_ed25519",
        "keys/id_ed25519.pub",
        "keys/id_ecdsa",
        "keys/id_ecdsa.pub",
        "keys/id_dsa",
        "keys/id_dsa.pub",
    ],
)
def test_blocks_common_openssh_key_names(file_path, monkeypatch, capsys):
    exit_code, captured = run_hook(
        {"tool_name": "Write", "tool_input": {"file_path": file_path}},
        monkeypatch,
        capsys,
    )

    assert exit_code == 2
    assert "BLOCKED" in captured.err
    assert file_path in captured.err


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
    exit_code, captured = run_hook_raw("{", monkeypatch, capsys)

    assert exit_code == 0
    assert "bad JSON payload" in captured.err


@pytest.mark.parametrize("payload_raw", ["[]", '"string"'])
def test_non_object_json_allows_and_reports_error(payload_raw, monkeypatch, capsys):
    exit_code, captured = run_hook_raw(payload_raw, monkeypatch, capsys)

    assert exit_code == 0
    assert "JSON payload must be an object" in captured.err


def expand_project_dir(command, project_dir):
    """Return ``command`` with ``$CLAUDE_PROJECT_DIR`` replaced by ``project_dir``.

    Args:
        command: Hook command template from Claude settings.
        project_dir: Repository path to substitute into the hook command.

    Returns:
        The shell command string to execute in tests.
    """
    return command.replace("$CLAUDE_PROJECT_DIR", str(project_dir))


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
        hook for hook in protected_entry["hooks"] if hook.get("type") == "command"
    ]

    assert commands == [
        {
            "type": "command",
            "command": '"$CLAUDE_PROJECT_DIR/.claude/hooks/protect-sensitive-files.py"',
        }
    ]


def test_registered_hook_command_blocks_sensitive_file():
    repo_root = Path(__file__).resolve().parents[1]
    settings = json.loads(
        (repo_root / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    command = expand_project_dir(
        settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"], repo_root
    )
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


def test_registered_hook_command_handles_project_dir_with_spaces(tmp_path):
    repo_root = Path(__file__).resolve().parents[1]
    linked_repo = tmp_path / "repo with spaces"
    try:
        linked_repo.symlink_to(repo_root, target_is_directory=True)
    except OSError as exc:
        pytest.skip("symlinks are unavailable in this test environment: {0}".format(exc))
    settings = json.loads(
        (repo_root / ".claude" / "settings.json").read_text(encoding="utf-8")
    )
    command = expand_project_dir(
        settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"], linked_repo
    )
    payload = json.dumps(
        {"tool_name": "Write", "tool_input": {"file_path": "secrets/.env"}}
    )

    result = subprocess.run(
        command,
        input=payload,
        text=True,
        capture_output=True,
        shell=True,
        env={**os.environ, "CLAUDE_PROJECT_DIR": str(linked_repo)},
        check=False,
    )

    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert "secrets/.env" in result.stderr
