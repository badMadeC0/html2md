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

def check_health():
    return run("python scripts/healthcheck.py")

def has_changes():
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(result.stdout.strip()) > 0

def main():
    if check_health():
        print("Project is already healthy. Exiting.")
        sys.exit(0)

    print("Project failing healthcheck, attempting self-heal...")

    # 1. Format code
    run("black .")

    if has_changes():
        if check_health():
            print("Self-heal successful (formatting applied).")
            sys.exit(0)
        else:
            print("Self-heal applied formatting, but healthcheck still failing.")
            sys.exit(1)

    print("Self-heal failed to fix the project or no changes were made.")
    sys.exit(1)

if __name__ == "__main__":
    main()
