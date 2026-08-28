#!/usr/bin/env python3
"""
Targeted repairs for the html2md Python project.
Attempts formatting, etc., then checks if healthcheck passes.
"""
import subprocess
import sys
import os
from pathlib import Path

def sh(cmd, cwd=None):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True, check=False, cwd=cwd)

def try_sh(cmd, cwd=None):
    try:
        print(f"\n$ {cmd}")
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError:
        return False

def changed():
    out = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    return len(out.stdout.strip()) > 0

def pass_health():
    rc = subprocess.run(f"{sys.executable} scripts/healthcheck.py", shell=True, check=False).returncode
    return rc == 0

def main():
    fixed = False

    # 1) Formatting
    try_sh("black .")
    if pass_health():
        fixed = fixed or changed()

    # 2) Snapshot updates (if applicable, using pytest-snapshot or similar, we just run pytest --snapshot-update if it exists)
    # We will just run pytest -q --snapshot-update if possible, but standard pytest doesn't have it unless plugin is installed.
    # We will skip or just run basic pytest.

    # 3) Lockfile repair/Dependency refresh
    if not pass_health():
        try_sh("pip install -e .")
        if pass_health():
            fixed = fixed or changed()

    # 4) Known generators
    if not pass_health():
        for script in ["scripts/update-icon-docs.py", "scripts/verify-static.py"]:
            if Path(script).exists():
                try_sh(f"{sys.executable} {script}")
        if pass_health():
            fixed = fixed or changed()

    if fixed and pass_health():
        print("[self-heal] Repairs successful and diff generated.")
        sys.exit(0)
    else:
        print("[self-heal] Repairs did not fully resolve issues or no changes needed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
