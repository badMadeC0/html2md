#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a Python repo.
"""
import subprocess
import sys
import os

def run(cmd):
    return subprocess.run(cmd, shell=True)

def try_run(name, cmd):
    if not cmd:
        return
    print(f"\n==> {name}")
    sys.stdout.flush()
    result = run(cmd)
    if result.returncode != 0:
        print(f"[healthcheck] {name} failed", file=sys.stderr)
        sys.exit(1)

def main():
    try:
        if os.path.exists("src") or os.path.exists("tests"):
            try_run("Format check", "black --target-version py38 --check src tests")
        try_run("Unit tests", "pytest -q")

        # Everything passed
        sys.exit(0)
    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
