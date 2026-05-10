#!/usr/bin/env python
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 if healthcheck passes after repair attempt; exit 1 if healthcheck still fails.
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

    if pass_health():
        print("\nHealthcheck passes after repair attempt.")
        sys.exit(0)

    print("\nHealthcheck still fails after repair attempt.")
    sys.exit(1)


if __name__ == "__main__":
    main()
