#!/usr/bin/env python3
"""Healthcheck for html2md: runs install verification, tests, lint, and import checks."""
from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str], label: str) -> bool:
    """Run a command, print its label, return True if it succeeds."""
    print(f"\n==> {label}")
    print(f"    $ {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=False)
        if result.returncode != 0:
            print(f"    FAILED (exit {result.returncode})")
            return False
        print(f"    OK")
        return True
    except FileNotFoundError:
        print(f"    FAILED (command not found)")
        return False


def check_tool_runnable(cmd: list[str]) -> bool:
    """Return True if the given command can be executed successfully."""
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def main(argv=None) -> int:
    ok = True

    # 1. Verify the package imports cleanly
    ok &= run(
        [sys.executable, "-c", "import html2md; print(html2md.__version__)"],
        "Import check",
    )

    # 2. Verify CLI --help exits 0
    ok &= run(
        [sys.executable, "-m", "html2md", "--help"],
        "CLI smoke (--help)",
    )

    # 3. Run the test suite
    if check_tool_runnable([sys.executable, "-m", "pytest", "--version"]):
        ok &= run(
            [sys.executable, "-m", "pytest", "-q"],
            "Test suite (pytest)",
        )
    else:
        print("\n==> Test suite (pytest)")
        print("    pytest not found, skipping tests (FAIL).")
        ok = False

    # 4. Lint with ruff (if available)
    ruff_label = "Lint (ruff check)"
    if check_tool_runnable([sys.executable, "-m", "ruff", "--version"]):
        ok &= run(
            [sys.executable, "-m", "ruff", "check", "."],
            ruff_label,
        )
    else:
        print(f"\n==> {ruff_label}")
        print("    Ruff not found, skipping linting (FAIL).")
        ok = False

    # 5. Verify package builds
    ok &= run(
        [sys.executable, "-m", "pip", "check"],
        "Dependency check (pip check)",
    )

    if ok:
        print("\n==> All healthchecks passed.")
    else:
        print("\n==> Some healthchecks FAILED.", file=sys.stderr)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
