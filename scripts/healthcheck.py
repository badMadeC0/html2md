#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a Python repository.
- Runs `pytest`
- Runs `black --check`
"""

import subprocess
import sys


def run(cmd):
    return subprocess.run(cmd, shell=True)


def try_run(name, cmd):
    print(f"\n==> {name}")
    result = run(cmd)
    return result.returncode == 0


def main():
    success = True

    if not try_run("Unit tests", "pytest -q"):
        print("[healthcheck] pytest failed")
        success = False

    if not try_run("Formatting check", "black --check ."):
        print("[healthcheck] black formatting check failed")
        success = False

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
