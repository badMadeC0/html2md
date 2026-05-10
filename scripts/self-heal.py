#!/usr/bin/env python
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 if repairs were applied and healthcheck passes; exit 1 otherwise.
"""
from __future__ import annotations

import subprocess
import sys


def sh(argv: list) -> None:
    print(f"\n$ {' '.join(str(a) for a in argv)}")
    subprocess.run(argv, check=True)


def try_sh(argv: list) -> bool:
    try:
        sh(argv)
        return True
    except Exception:
        return False


def changed() -> bool:
    out = subprocess.check_output(["git", "status", "--porcelain"], encoding="utf-8")
    return len(out.strip()) > 0


def pass_health() -> bool:
    try:
        subprocess.run(
            [sys.executable, "scripts/healthcheck.py"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main() -> None:
    # 1) Lint/format auto-fix
    try_sh([sys.executable, "-m", "black", "src", "tests"])

    if pass_health() and changed():
        print("\nRepairs applied and healthcheck passes.")
        sys.exit(0)

    print("\nNo repairs were successfully applied or healthcheck still fails.")
    sys.exit(1)


if __name__ == "__main__":
    main()
