#!/usr/bin/env python3
"""
Targeted, ordered repairs for html2md-cli.
Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""

import subprocess
import sys

def run(cmd):
    """Run a command and stream output. Return True if success, False otherwise."""
    print(f"\n$ {cmd}")
    result = subprocess.run(cmd, shell=True)
    return result.returncode == 0

def changed():
    """Return True if there are uncommitted changes (git status)."""
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(result.stdout.strip()) > 0

def pass_health():
    """Return True if the healthcheck passes."""
    # use the current python interpreter
    cmd = f"{sys.executable} scripts/healthcheck.py"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode == 0

def main():
    fixed = False

    # 1) Lint/format auto-fix
    print("Attempting to fix formatting with black...")
    run(f"{sys.executable} -m black .")

    if pass_health():
        if changed():
            fixed = True
            print("Formatting fixes applied and healthcheck passed.")

    if fixed:
        sys.exit(0)
    else:
        print("No successful repairs could be applied or no changes were needed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
