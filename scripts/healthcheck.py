#!/usr/bin/env python3
"""Healthcheck for html2md: runs install verification, tests, lint, and import checks."""
from __future__ import annotations

import subprocess
import sys


def run(cmd: list[str], label: str) -> bool:
    """Run a command, print its label, return True if it succeeds."""
    print(f"\n==> {label}")
    print(f"    $ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"    FAILED (exit {result.returncode})")
        return False
    print(f"    OK")
    return True


def check_tool_exists(cmd: list[str]) -> bool:
    """Check if a tool exists by running it and verifying success."""
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
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
    ok &= run(
        [sys.executable, "-m", "pytest", "-q"],
        "Test suite (pytest)",
    )

    # 4. Lint with ruff (if available)
    ruff_label = "Lint (ruff check)"
    if check_tool_exists([sys.executable, "-m", "ruff", "--version"]):
        ok &= run(
            [sys.executable, "-m", "ruff", "check", "src/", "tests/"],
            ruff_label,
        )
    else:
        print(f"\n==> {ruff_label}")
        print("    Ruff not found, skipping linting.")

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
