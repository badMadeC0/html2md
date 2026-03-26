#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a python project:
   - root: format check? test?
"""
import subprocess
import sys
import os

def run_cmd(cmd: str, name: str) -> bool:
    print(f"\n==> {name}")
    try:
        # Run command and inherit stdout/stderr
        result = subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    success = True

    # 1. Format check (black)
    if not run_cmd("black --check src tests scripts", "Format Check (black)"):
        print("[healthcheck] Format check failed.")
        success = False

    # 2. Unit tests (pytest)
    if not run_cmd("pytest -q", "Unit Tests (pytest)"):
        print("[healthcheck] Unit tests failed.")
        success = False

    if not success:
        sys.exit(1)

    print("\n[healthcheck] All checks passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
