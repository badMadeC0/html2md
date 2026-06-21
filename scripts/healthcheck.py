#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a python project:
   - root: typecheck (mypy - if available)? test (pytest)? lint (black --check)?
"""
import subprocess
import sys
import os

def run(cmd, env=None):
    return subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)

def has_tool(name):
    from shutil import which
    return which(name) is not None

def try_run(name, cmd):
    if not cmd:
        return True
    print(f"\n==> {name}")
    print(f"$ {cmd}")
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    result = run(cmd, env=env)
    if result.returncode != 0:
        print(result.stdout)
        print(f"[{name}] failed with code {result.returncode}")
        return False
    print("OK")
    return True

def main():
    success = True

    # Root-level checks
    if has_tool("black"):
        success = success and try_run("Format Check (black)", "black --check src tests")

    if has_tool("pytest"):
        success = success and try_run("Unit tests (pytest)", "pytest -q")

    if not success:
        sys.exit(1)

    print("\nHealthcheck passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
