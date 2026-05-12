#!/usr/bin/env python3
import subprocess
import sys
import os

def run_cmd(cmd, cwd=None, env=None):
    print(f"\n==> Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env)
        return True
    except subprocess.CalledProcessError:
        print(f"[healthcheck] Command failed: {cmd}")
        return False

def main():
    success = True

    # Use PYTHONPATH=src to ensure modules can be found if not fully installed
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"

    # Check formatting
    if not run_cmd("black --check src tests", env=env):
        success = False

    # Run tests
    if not run_cmd("pytest -q", env=env):
        success = False

    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
