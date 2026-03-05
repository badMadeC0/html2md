#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""

import subprocess
import sys
import os


def sh(cmd):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def changed():
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return len(out.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def pass_health():
    try:
        # Run healthcheck
        sh("python scripts/healthcheck.py")
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    fixed = False

    # 1) Lint/format auto-fix
    try_sh("black .")

    if pass_health():
        fixed = fixed or changed()

    # (Other repairs can be added here, like snapshot updates if pytest-snapshot is used,
    # dependency type sync if using mypy, etc.)

    # 2) Dependencies (requirements sync or upgrade, though for this simple case maybe not needed)

    if fixed:
        print("\n[self-heal] Repairs succeeded and produced a diff.")
        sys.exit(0)
    else:
        print("\n[self-heal] Repairs did not fully succeed or produced no diff.")
        sys.exit(1)


if __name__ == "__main__":
    main()
