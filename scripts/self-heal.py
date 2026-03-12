#!/usr/bin/env python3
"""
Targeted, ordered repairs. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
import subprocess
import sys
import os

def sh(cmd):
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result

def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except Exception as e:
        print(f"Failed to execute {' '.join(cmd)}: {e}")
        return False

def changed():
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return len(out.stdout.strip()) > 0

def pass_health():
    # Run the healthcheck script using sys.executable so it matches the current environment
    healthcheck_script = os.path.join(os.path.dirname(__file__), "healthcheck.py")
    try:
        result = subprocess.run([sys.executable, healthcheck_script])
        return result.returncode == 0
    except Exception:
        return False

def main():
    fixed = False

    # 1) Format with black
    print("\n[self-heal] Attempting format repair")
    try_sh([sys.executable, "-m", "black", "src", "tests"])

    if pass_health():
        fixed = fixed or changed()

    if fixed:
        print("\n[self-heal] Successfully applied fixes.")
        sys.exit(0)
    else:
        print("\n[self-heal] No fixes applied or healthcheck still failing.")
        sys.exit(1)

if __name__ == "__main__":
    main()
