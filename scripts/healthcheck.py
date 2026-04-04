#!/usr/bin/env python3
"""
Minimal healthcheck for the html2md repo:
- runs formatting checks (black)
- runs unit tests (pytest)
"""
import subprocess
import sys
import os

def run(cmd):
    return subprocess.run(cmd, shell=True, text=True)

def try_run(name, cmd):
    if not cmd:
        return
    print(f"\n==> {name}")
    try:
        # if windows, we may need to use shell=True and handle paths, but we try standard run
        res = subprocess.run(cmd, shell=True)
        if res.returncode != 0:
            print(f"[{name}] failed")
            sys.exit(1)
    except Exception as e:
        print(f"[{name}] failed: {e}")
        sys.exit(1)

def main():
    try:
        # Check formatting with black
        try_run("Check Formatting", "black --check src tests")

        # Unit tests
        try_run("Unit tests", "PYTHONPATH=src pytest -q")

        sys.exit(0)
    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
