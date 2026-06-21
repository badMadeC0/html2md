#!/usr/bin/env python3
"""
Targeted, ordered repairs for a python project. Each step is idempotent and re-runs healthcheck.
Exit 0 only if a repair produced a passing healthcheck and a non-empty diff.
"""
import subprocess
import sys
import os

def run(cmd, env=None):
    print(f"\n$ {cmd}")
    return subprocess.run(cmd, shell=True, check=False, stdout=sys.stdout, stderr=sys.stderr, text=True, env=env)

def try_run(cmd, env=None):
    try:
        result = subprocess.run(cmd, shell=True, check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        if result.returncode == 0:
            print(f"\n$ {cmd} (OK)")
            return True
        else:
            print(f"\n$ {cmd} (Failed with code {result.returncode})")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"\n$ {cmd} (Error: {e})")
        return False

def changed():
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return len(out.strip()) > 0
    except Exception:
        return False

def pass_health():
    env = os.environ.copy()
    env["PYTHONPATH"] = "src"
    try:
        result = subprocess.run([sys.executable, "scripts/healthcheck.py"], check=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
        return result.returncode == 0
    except Exception:
        return False

def main():
    fixed = False

    # 1) Format using black
    print("Attempting to run black for formatting repairs...")
    try_run("black src tests")
    if pass_health():
        fixed = fixed or changed()

    if fixed and pass_health():
        print("\nSelf-heal successful and healthcheck passes.")
        sys.exit(0)

    print("\nSelf-heal did not produce a passing healthcheck with diffs.")
    sys.exit(1)

if __name__ == "__main__":
    main()
