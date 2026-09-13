#!/usr/bin/env python3
"""Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
import subprocess
import sys

def sh(cmd: list[str]) -> subprocess.CompletedProcess:
    print(f"\n$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True)

def try_sh(cmd: list[str]) -> bool:
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def changed() -> bool:
    try:
        out = subprocess.run(["git", "status", "--untracked-files=no", "--porcelain"], capture_output=True, text=True, check=True)
        return len(out.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def pass_health() -> bool:
    try:
        subprocess.run([sys.executable, "scripts/healthcheck.py"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def main() -> None:
    fixed = False

    # 1) Lint/format
    try_sh(["black", "."])
    if pass_health():
        fixed = fixed or changed()

    # If health check doesn't pass after simple formatting, exit with an error.
    # The workflow relies on self-heal.py to attempt fixes, but the real
    # measure of success is the final healthcheck.py run.
    if pass_health() and fixed:
        sys.exit(0)
    else:
        # Either not fixed or healthcheck failed
        sys.exit(1)

if __name__ == "__main__":
    main()
