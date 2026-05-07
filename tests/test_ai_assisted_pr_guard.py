import os
import subprocess
import textwrap
from pathlib import Path


WORKFLOW_PATH = Path(__file__).resolve().parents[1] / ".github/workflows/ai-assisted-pr-guard.yml"


def _guard_script() -> str:
    workflow = WORKFLOW_PATH.read_text()
    _, run_block = workflow.split("        run: |\n", 1)
    lines = []
    for line in run_block.splitlines():
        if line.startswith("          ") or not line:
            lines.append(line)
            continue
        break
    return textwrap.dedent("\n".join(lines))


def _run_guard(title: str, body: str = "") -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update({"PR_TITLE": title, "PR_BODY": body})
    return subprocess.run(
        ["bash", "-c", _guard_script()],
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
    assert "does not include a Claude chat URL" in result.stdout


def test_tagged_prs_with_accepted_transcript_links_pass():
    result = _run_guard(
        "[AI-Assisted] Fix parser edge case",
        "Transcript: https://claude.ai/chat/2c4f3e25-4e34-4dfd-b186-341a40a491f0",
    )

    assert result.returncode == 0, result.stderr
    assert "contains an agent chat URL" in result.stdout
