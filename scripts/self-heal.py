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
    sys.stdout.flush()
    return subprocess.run(cmd, shell=True, **kwargs)

def try_sh(cmd, **kwargs):
    try:
        res = sh(cmd, **kwargs)
        return res.returncode == 0
    except Exception:
        return False

def changed():
    out = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(out.stdout.strip()) > 0

def pass_health():
    try:
        res = sh("python scripts/healthcheck.py")
        return res.returncode == 0
    except Exception:
        return False

def main():
    fixed = False

    # 1) Lint/format
    if os.path.exists("src") or os.path.exists("tests"):
        try_sh("black --target-version py38 src tests")
        if pass_health():
            fixed = fixed or changed()

    # If it passes healthcheck and there are changes, we fixed it.
    if fixed and pass_health() and changed():
        print("\n[self-heal] Repairs successful and diff generated.", file=sys.stderr)
        sys.exit(0)
    elif pass_health() and not changed():
        print("\n[self-heal] Healthcheck passes, but no changes were made.", file=sys.stderr)
        sys.exit(1) # exit 1 to not open a PR
    else:
        print("\n[self-heal] Healthcheck still failing or no repairs were successful.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
