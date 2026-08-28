#!/usr/bin/env python3
"""
Minimal healthcheck for the html2md Python project.
Runs pytest on root and checks apps/* and packages/* if they exist.
Exits with a non-zero code if anything fails.
"""
import subprocess
import sys
import os
from pathlib import Path

def run_cmd(cmd, cwd=None):
    print(f"\n==> {cmd} (cwd: {cwd or '.'})")
    env = os.environ.copy()
    if not cwd or cwd == ".":
        env["PYTHONPATH"] = "src"
    result = subprocess.run(cmd, shell=True, env=env, cwd=cwd)
    return result.returncode

def main():
    print("Running healthcheck...")

    # 1. Root-level checks
    test_rc = run_cmd(f"{sys.executable} -m pytest -q")
    if test_rc != 0:
        print("[healthcheck] root tests failed")
        sys.exit(test_rc)

    # 2. Workspace smoke builds/tests
    roots = ["apps", "packages"]
    for base in roots:
        base_path = Path(base)
        if not base_path.exists():
            continue
        for child in base_path.iterdir():
            if not child.is_dir():
                continue

            print(f"\nChecking workspace: {child}")
            # If pyproject.toml exists, test or build
            if (child / "pyproject.toml").exists() or (child / "setup.py").exists():
                rc = run_cmd(f"{sys.executable} -m pytest -q", cwd=str(child))
                if rc != 0 and rc != 5:  # 5 means no tests collected, which is fine
                    print(f"[healthcheck] tests failed in {child}")
                    sys.exit(1)

    print("[healthcheck] All checks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
