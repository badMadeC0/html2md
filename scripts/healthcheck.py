#!/usr/bin/env python
"""
Minimal healthcheck for a Python repository.
Runs formatting checks and unit tests.
"""
from __future__ import annotations

import os
import subprocess
import sys


def run_cmd(name: str, argv: list) -> None:
    print(f"\n==> {name}")
    try:
        subprocess.run(argv, check=True)
    except subprocess.CalledProcessError:
        print(f"[{name}] failed")
        sys.exit(1)


def main() -> None:
    # Append src to PYTHONPATH so the package is importable without pip install -e .
    src = os.path.join(os.getcwd(), "src")
    existing = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = src if not existing else f"{existing}{os.pathsep}{src}"

    # Black check — use sys.executable so the same Python env is used
    run_cmd("Formatting (Black)", [sys.executable, "-m", "black", "--check", "src", "tests"])

    # Pytest check
    run_cmd("Unit tests", [sys.executable, "-m", "pytest", "-q"])

    print("\nAll healthchecks passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
