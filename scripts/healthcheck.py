#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a Python repo.
Checks:
- Linting/formatting (black)
- Tests (pytest)
"""
import subprocess
import sys

def run(cmd, name):
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"[{name}] failed")
        sys.exit(1)

def main():
    print("Starting healthcheck...")

    # Check black formatting without modifying
    run("python -m black --check src tests", "Black format check")

    # Run tests
    run("python -m pytest -q", "Unit tests")

    print("\nHealthcheck passed!")

if __name__ == "__main__":
    main()
