#!/usr/bin/env python3
"""
Targeted, ordered repairs for a Python repo.
Attempts fixes and exits successfully if a fix restores health.
"""
import subprocess
import sys

def sh(cmd):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True)

def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except Exception:
        return False

def changed():
    out = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(out.stdout.strip()) > 0

def pass_health():
    try:
        result = subprocess.run("python scripts/healthcheck.py", shell=True, capture_output=True)
        return result.returncode == 0
    except Exception:
        return False

def main():
    fixed = False

    # 1) Format with black
    print("Attempting to fix formatting...")
    try_sh("python -m black src tests")

    if pass_health():
        fixed = fixed or changed()

    if fixed:
        print("Self-heal successfully applied fixes that restored health.")
        sys.exit(0)
    else:
        print("Self-heal was unable to restore health or no changes were made.")
        sys.exit(1)

if __name__ == "__main__":
    main()
