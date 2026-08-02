#!/usr/bin/env python3
import subprocess
import sys
import os

def run(cmd):
    print(f"\n==> {cmd}")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = subprocess.run(cmd, shell=True, env=env)
    return result.returncode == 0

def main():
    success = True

    # Run tests
    if not run("pytest -q"):
        print("[healthcheck] tests failed")
        success = False

    if not success:
        sys.exit(1)

    print("[healthcheck] all checks passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
