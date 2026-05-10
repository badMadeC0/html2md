"""Regression tests for the self-heal workflow."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "self-heal.yml"


def _workflow_source() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_workflow_run_checkout_uses_branch_not_detached_sha():
    """workflow_run repairs must be based on the failed branch, not a detached SHA."""
    source = _workflow_source()

    assert "github.event.workflow_run.head_sha" not in source
    assert (
        "ref: ${{ github.event_name == 'workflow_run' && "
        "github.event.workflow_run.head_branch || github.ref }}"
    ) in source


def test_create_pull_request_sets_explicit_base_for_workflow_run():
    """create-pull-request needs an explicit base after workflow_run branch checkout."""
    source = _workflow_source()

    assert (
        "base: ${{ github.event_name == 'workflow_run' && "
        "github.event.workflow_run.head_branch || github.ref_name }}"
    ) in source
    assert "branch: auto-heal/fixes" in source
