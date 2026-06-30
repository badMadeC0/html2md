#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for the python repo:
- Runs `pytest -q`
- Runs `black --check .`
"""

import subprocess
import sys


def run_cmd(name, cmd):
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"[healthcheck] {name} failed")
        return False
    return True


def main():
    success = True

    # Run tests
    if not run_cmd("Unit tests", ["pytest", "-q"]):
        success = False

    # Run formatting check
    if not run_cmd("Format check", ["black", "--check", "."]):
        success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
