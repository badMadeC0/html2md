"""Regression tests for the self-heal GitHub Actions workflow."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF_HEAL_WORKFLOW = ROOT / ".github" / "workflows" / "self-heal.yml"


def _workflow_step(name: str) -> str:
    """Return the text block for a named workflow step."""
    source = SELF_HEAL_WORKFLOW.read_text(encoding="utf-8")
    marker = f"      - name: {name}\n"
    start = source.index(marker)
    next_step = source.find("\n      - name: ", start + len(marker))
    if next_step == -1:
        return source[start:]
    return source[start:next_step]


def test_self_heal_repair_step_preserves_command_failures():
    """The repair command is piped through tee, so pipefail must preserve failures."""
    repair_step = _workflow_step("Attempt self-heal repairs")

    assert "set -o pipefail" in repair_step
    assert "node scripts/self-heal.mjs | tee selfheal-repair.txt" in repair_step
    assert repair_step.index("set -o pipefail") < repair_step.index(
        "node scripts/self-heal.mjs | tee selfheal-repair.txt"
    )
