#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
import subprocess
import sys
import os

def run_cmd(cmd: str) -> bool:
    print(f"\n$ {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def try_cmd(cmd: str) -> bool:
    return run_cmd(cmd)

def has_changes() -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=True
        )
        return len(result.stdout.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def pass_health() -> bool:
    try:
        subprocess.run(["python", "scripts/healthcheck.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    fixed = False

    # 1. Formatting auto-fix (black)
    try_cmd("black src tests scripts")

    if pass_health():
        if has_changes():
            fixed = True

    # Check if fix produced a passing state with changes
    if fixed:
        print("\n[self-heal] Repairs successful and generated diff.")
        sys.exit(0)
    else:
        print("\n[self-heal] Repairs failed or no diff generated.")
        sys.exit(1)

if __name__ == "__main__":
    main()
