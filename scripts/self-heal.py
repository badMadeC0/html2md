#!/usr/bin/env python3
import subprocess
import sys
import os

def run_cmd(cmd):
    print(f"\n$ {cmd}")
    return subprocess.run(cmd, shell=True)

def try_cmd(cmd):
    try:
        run_cmd(cmd)
        return True
    except Exception:
        return False

def has_changes():
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(result.stdout.strip()) > 0

def pass_health():
    try:
        result = subprocess.run("python scripts/healthcheck.py", shell=True)
        return result.returncode == 0
    except Exception:
        return False

def main():
    fixed = False

    # 1) Format using black
    try_cmd("black src tests")

    if pass_health():
        fixed = fixed or has_changes()

    if not fixed:
        print("\n[self-heal] No changes were made or healthcheck still fails.")
        sys.exit(1)

    print("\n[self-heal] Changes applied successfully and healthcheck passed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
