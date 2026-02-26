#!/usr/bin/env python3
"""Targeted, ordered repairs for html2md.

Each step is idempotent and re-runs the healthcheck after changes.
Exit 0 if the healthcheck eventually passes, regardless of whether any files changed.
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
    )
    return bool(result.stdout.strip())


def passes_healthcheck() -> bool:
    """Return True if scripts/healthcheck.py exits 0."""
    # We call the healthcheck script using the same python interpreter
    result = subprocess.run([sys.executable, "scripts/healthcheck.py"])
    return result.returncode == 0


def fix_dependencies() -> bool:
    """Install/upgrade dependencies and dev tools."""
    ok = True
    ok &= sh([sys.executable, "-m", "pip", "install", "-e", "."], "editable install")
    ok &= sh([sys.executable, "-m", "pip", "install", "pytest", "ruff"], "install dev tools")
    return ok


def fix_lint() -> bool:
    """Run ruff linting and formatting fixes."""
    ok = True
    # We target src/ and tests/ explicitly to match typical usage,
    # but "." is also fine if ruff defaults are set.
    # Using "." to catch everything including scripts/.
    ok &= sh([sys.executable, "-m", "ruff", "check", "--fix", "."], "ruff fix")
    ok &= sh([sys.executable, "-m", "ruff", "format", "."], "ruff format")
    return ok


def fix_install(force: bool = False) -> bool:
    """Force reinstall if needed."""
    flags = ["--upgrade"]
    if force:
        flags.append("--force-reinstall")
    return sh(
        [sys.executable, "-m", "pip", "install"] + flags + ["-e", "."],
        "reinstall deps" if force else "upgrade deps",
    )


def main() -> int:
    """Run repair steps sequentially, but stop if healthcheck starts passing."""
    if passes_healthcheck():
        print("\n=== Healthcheck already passes. ===")
        return 0

    print("\n=== Step 1: Install Dependencies ===")
    fix_dependencies()
    if passes_healthcheck():
        print("\n=== Fixed by installing dependencies. ===")
        # If fixed, we exit 0 regardless of changes
        return 0

    print("\n=== Step 2: Lint/Format Auto-fix ===")
    fix_lint()
    if passes_healthcheck():
        print("\n=== Fixed by linting/formatting. ===")
        return 0

    print("\n=== Step 3: Upgrade Dependencies ===")
    fix_install(force=False)
    if passes_healthcheck():
        print("\n=== Fixed by upgrading dependencies. ===")
        return 0

    print("\n=== Step 4: Force Reinstall ===")
    fix_install(force=True)
    if passes_healthcheck():
        print("\n=== Fixed by force reinstall. ===")
        return 0

    print("\n=== Self-heal could not fix all issues. ===", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
