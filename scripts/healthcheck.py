#!/usr/bin/env python3
"""
Minimal, opinionated healthcheck for a Python project:
- Typecheck (optional, currently disabled as not explicitly in instructions but good to have a placeholder)
- Lint/format check (black)
- Unit tests (pytest)
"""
import subprocess
import sys
import shutil

def run(cmd):
    print(f"\n==> {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"[healthcheck] command failed: {' '.join(cmd)}")
        return False
    return True

def try_run(name, cmd):
    if not cmd:
        return True

    # check if tool exists
    tool = cmd[0]
    if tool == 'python' or tool == 'python3':
        tool_to_check = cmd[2] if cmd[1] == '-m' else cmd[1]
    else:
        tool_to_check = tool

    # Just run it, the subprocess will fail if the module is missing
    print(f"\n==> {name}")
    try:
        result = subprocess.run(cmd)
        if result.returncode != 0:
            print(f"[healthcheck] {name} failed")
            return False
        return True
    except FileNotFoundError:
        print(f"[healthcheck] Tool not found for {name}: {cmd[0]}")
        return False

def main():
    success = True

    # Root-level checks
    if not try_run("Format check (black)", ["python", "-m", "black", "--check", "src", "tests"]):
        success = False

    if not try_run("Unit tests", ["pytest", "-q"]):
        success = False

    if not success:
        sys.exit(1)

    print("\n[healthcheck] All checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
