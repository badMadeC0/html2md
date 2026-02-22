#!/usr/bin/env python3
"""Targeted, ordered repairs for html2md.

Each step is idempotent and re-runs the healthcheck after changes.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
from __future__ import annotations

import subprocess
import sys


def sh(cmd: list[str], label: str) -> bool:
    """Run a command, return True on success."""
    print(f"\n$ {' '.join(cmd)}  # {label}")
    result = subprocess.run(cmd)
    return result.returncode == 0


def has_changes() -> bool:
    """Return True if the working tree has uncommitted changes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=True,
    )
    return bool(result.stdout.strip())


def passes_healthcheck() -> bool:
    """Return True if scripts/healthcheck.py exits 0."""
    result = subprocess.run([sys.executable, "scripts/healthcheck.py"])
    return result.returncode == 0


def main(argv: list[str] | None = None) -> int:
    fixed = False

    if passes_healthcheck():
        print("Fixed after re-install.")
        fixed = fixed or has_changes()
        if fixed:
            return 0

    # 2. Lint/format auto-fix with ruff
    print("\n=== Step 2: Lint/format auto-fix ===")
    sh([sys.executable, "-m", "ruff", "check", "--fix", "src/", "tests/"], "ruff fix")
    sh([sys.executable, "-m", "ruff", "format", "src/", "tests/"], "ruff format")
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("Fixed after lint/format.")
            return 0

    # 3. Upgrade dependencies (may fix version conflicts)
    print("\n=== Step 3: Dependency upgrade ===")
    sh(
        [sys.executable, "-m", "pip", "install", "--upgrade", "-e", "."],
        "upgrade deps",
    )
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("Fixed after dependency upgrade.")
            return 0

    # 4. Rebuild package metadata (clean + reinstall)
    print("\n=== Step 4: Clean reinstall ===")
    sh(
        [sys.executable, "-m", "pip", "install", "--force-reinstall", "-e", "."],
        "force reinstall",
    )
    if passes_healthcheck():
        fixed = fixed or has_changes()
        if fixed:
            print("Fixed after clean reinstall.")
            return 0

    # If nothing worked, report failure
    if not passes_healthcheck():
        print("\n=== Self-heal could not fix all issues. ===", file=sys.stderr)
        return 1

    if not has_changes():
        print("\n=== Healthcheck passes but no file changes to commit. ===")
        return 1

    print("\n=== Repairs applied successfully. ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
