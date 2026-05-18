#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""

import subprocess
import sys


def sh(cmd: str) -> None:
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(result.returncode, cmd)


def try_sh(cmd: str) -> bool:
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def changed() -> bool:
    result = subprocess.run(
        "git status --porcelain", shell=True, capture_output=True, text=True
    )
    return len(result.stdout.strip()) > 0


def pass_health() -> bool:
    try:
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

    if fixed:
        sys.exit(0)
    else:
        # Exit non-zero if no fix was found that passed the health check or there was no diff
        sys.exit(1)


if __name__ == "__main__":
    main()
