"""Regression tests for the repository healthcheck script."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HEALTHCHECK = ROOT / "scripts" / "healthcheck.mjs"


def test_healthcheck_avoids_pnpm_workspace_flags():
    """The repo is not a pnpm workspace, so workspace-root flags must not be used."""
    source = HEALTHCHECK.read_text(encoding="utf-8")

    assert "pnpm -w" not in source
    assert "--workspace-root" not in source
