#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for the python repository.
- runs pytest
- runs black --check
"""

import subprocess
import sys


def run(cmd: str) -> None:
    print(f"\n==> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"[healthcheck] command failed: {cmd}", file=sys.stderr)
        sys.exit(result.returncode)


def main():
    try:
        # Code formatting check
        run("black --check .")

        # Tests
        # Ensure that test suite passes
        run("PYTHONPATH=src pytest -q")

        sys.exit(0)
    except Exception as e:
        print(f"[healthcheck] exception: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
