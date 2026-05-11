from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

import pytest


WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github/workflows/ai-assisted-pr-guard.yml"


def _guard_script() -> str:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
    _, step_block = workflow.split("      - name: Inspect PR title and body\n", 1)
    _, run_block = step_block.split("        run: |\n", 1)
    lines = []
    for line in run_block.splitlines():
        if line.startswith("          ") or not line:
            lines.append(line)
            continue
        break
    return textwrap.dedent("\n".join(lines))


def _run_guard(title: str, body: str = "", draft: bool = False) -> subprocess.CompletedProcess[str]:
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("workflow guard script uses bash syntax")

    env = os.environ.copy()
    env.update({"PR_TITLE": title, "PR_BODY": body, "PR_DRAFT": str(draft).lower()})
    return subprocess.run(
        [bash, "-c", _guard_script()],
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_untagged_prs_skip_ai_assisted_checks_successfully():
    result = _run_guard("Fix parser edge case")

    assert result.returncode == 0, result.stderr
    assert "skipping AI-assisted transcript checks" in result.stdout


def test_tagged_prs_still_require_transcript_links():
    result = _run_guard("[AI-Assisted] Fix parser edge case")

    assert result.returncode == 1
    assert "does not include an accepted agent chat URL" in result.stdout


def test_draft_tagged_prs_may_temporarily_use_transcript_placeholder():
    result = _run_guard(
        "[AI-Assisted] Fix parser edge case",
        "Transcript: <CLAUDE_CHAT_URL>",
        draft=True,
    )

    assert result.returncode == 0, result.stderr
    assert "Draft PR body still contains the <CLAUDE_CHAT_URL> placeholder" in result.stdout


def test_ready_tagged_prs_reject_transcript_placeholder():
    result = _run_guard(
        "[AI-Assisted] Fix parser edge case",
        "Transcript: <CLAUDE_CHAT_URL>",
    )

    assert result.returncode == 1
    assert "Replace it with a real agent chat URL before merging" in result.stdout


def test_tagged_prs_with_accepted_transcript_links_pass():
    result = _run_guard(
        "[AI-Assisted] Fix parser edge case",
        "Transcript: https://claude.ai/chat/2c4f3e25-4e34-4dfd-b186-341a40a491f0",
    )

    assert result.returncode == 0, result.stderr
    assert "contains an agent chat URL" in result.stdout


def test_tagged_prs_reject_lookalike_transcript_hosts():
    result = _run_guard(
        "[AI-Assisted] Fix parser edge case",
        "Transcript: https://claude.ai.evil.example/chat/not-real",
    )

    assert result.returncode == 1
    assert "does not include an accepted agent chat URL" in result.stdout
