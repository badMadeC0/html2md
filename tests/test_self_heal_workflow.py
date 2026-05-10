"""Regression tests for the self-heal workflow."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SELF_HEAL_WORKFLOW = ROOT / ".github" / "workflows" / "self-heal.yml"


def test_self_heal_repair_branch_includes_triggering_branch():
    """Auto-heal PR branches must be isolated by the failing source branch."""
    source = SELF_HEAL_WORKFLOW.read_text(encoding="utf-8")

    assert "branch: auto-heal/fixes" not in source
    assert "github.event.workflow_run.head_branch" in source
    assert "github.ref_name" in source
    assert (
        "branch: auto-heal/${{ github.event_name == 'workflow_run' && "
        "github.event.workflow_run.head_branch || github.ref_name }}"
    ) in source
