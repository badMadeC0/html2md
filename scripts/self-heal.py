#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
import subprocess
import sys
import os

def sh(cmd, **kwargs):
    print(f"\n$ {cmd}")
    return subprocess.run(cmd, shell=True, check=True, text=True, **kwargs)

def try_sh(cmd, **kwargs):
    try:
        sh(cmd, **kwargs)
        return True
    except subprocess.CalledProcessError:
        return False

def changed():
    try:
        # Check for modified tracked files, or new tracked files added
        # Exclude untracked files from the check so log artifacts don't trigger it
        out = subprocess.run("git status --untracked-files=no --porcelain", shell=True, check=True, text=True, capture_output=True)
        return len(out.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def pass_health():
    try:
        sh("python scripts/healthcheck.py")
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    fixed = False

    # 1) Lint/format
    print("\n[self-heal] Attempting format...")
    try_sh("python -m black .")

    if pass_health():
        fixed = fixed or changed()

    if fixed:
        print("\n[self-heal] Fixed issues successfully.")
        sys.exit(0)
    else:
        print("\n[self-heal] No fixes applied or healthcheck still failing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
