from pathlib import Path


WORKFLOW = Path(".github/workflows/self-heal.yml")


def workflow_text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_self_heal_uses_trusted_driver_for_repo_local_scripts():
    text = workflow_text()

    assert "path: self-heal-driver" in text
    assert "ref: ${{ github.event.repository.default_branch }}" in text
    assert "path: worktree" in text

    assert "node ../self-heal-driver/scripts/healthcheck.mjs" in text
    assert "node ../self-heal-driver/scripts/self-heal.mjs" in text
    assert "node scripts/healthcheck.mjs" not in text
    assert "node scripts/self-heal.mjs" not in text


def test_self_heal_verifies_driver_scripts_before_failed_ref_checkout():
    text = workflow_text()

    verify_step = text.index("- name: Verify trusted repair driver")
    failed_checkout = text.index("- name: Checkout failed ref")

    assert verify_step < failed_checkout
    assert "test -f self-heal-driver/scripts/healthcheck.mjs" in text
    assert "test -f self-heal-driver/scripts/self-heal.mjs" in text
