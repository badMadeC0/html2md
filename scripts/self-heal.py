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
    return subprocess.run(cmd, shell=True, text=True, **kwargs)

def try_sh(cmd, **kwargs):
    try:
        sh(cmd, check=True, **kwargs)
        return True
    except subprocess.CalledProcessError:
        return False

def changed():
    res = subprocess.run("git status --porcelain", shell=True, text=True, capture_output=True)
    return len((res.stdout or "").strip()) > 0

def pass_health():
    res = subprocess.run("python scripts/healthcheck.py", shell=True)
    return res.returncode == 0

def main():
    fixed = False

    # 1) Lint/format auto-fix
    try_sh("black src tests")
    if pass_health():
        fixed = fixed or changed()

    # (If we had snapshot updates, we'd add them here)

    # Note: For this basic setup, exit 0 if any repair succeeded (fixed is True)
    if fixed:
        print("\nSelf-healing successful and diff generated.")
        sys.exit(0)
    else:
        print("\nSelf-healing did not generate any new valid fixes.")
        sys.exit(1)

if __name__ == "__main__":
    main()
