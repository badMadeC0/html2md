#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for html2md-cli.
Runs the pytest test suite to ensure the project is healthy.
Exits 0 if healthy, non-zero if broken.
"""

import subprocess
import sys

def run(cmd):
    """Run a command and stream output. Return True if success, False otherwise."""
    print(f"\n==> {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def main():
    healthy = True
    print("Running healthcheck...")

    if not run("pytest -q"):
        print("[healthcheck] Unit tests failed.")
        healthy = False

    if not healthy:
        sys.exit(1)

    print("Healthcheck passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
