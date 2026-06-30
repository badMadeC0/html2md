#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""

import subprocess
import sys


def sh(cmd):
    print(f"\n$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def changed():
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"], capture_output=True, text=True, check=True
        )
        return len(result.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def pass_health():
    try:
        sh(["python", "scripts/healthcheck.py"])
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    fixed = False

    # 1) Format
    try_sh(["black", "."])

    if pass_health():
        fixed = fixed or changed()

    if fixed:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
