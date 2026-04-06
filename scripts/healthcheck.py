#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a Python repository.
- Root: pytest
"""
import subprocess
import sys

def run(cmd):
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        return False
    return True

def try_run(name, cmd):
    if not cmd:
        return True
    print(f"\n==> {name}")
    return run(cmd)

def main():
    success = True

    # Root-level checks
    if not try_run("Unit tests", "pytest -q"):
        print("[healthcheck] pytest failed")
        success = False

    if not success:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
