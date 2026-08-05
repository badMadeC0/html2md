import sys
import subprocess
import os

def sh(cmd):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)

def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False

def has_changes():
    try:
        out = subprocess.check_output(["git", "status", "--porcelain"], text=True)
        return len(out.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def pass_health():
    try:
        subprocess.run([sys.executable, "scripts/healthcheck.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    fixed = False

    # 1. Format code using black
    if try_sh("black src tests"):
        if pass_health():
            fixed = fixed or has_changes()

    # 2. Dependency updates/install (fallback or lockfile repair if this was pipenv/poetry)
    # Since this is standard pip/setup.py, we can just ensure dependencies are installed
    if not pass_health():
        if try_sh("python -m pip install -e . pytest black"):
            if pass_health():
                fixed = fixed or has_changes()

    # 3. Known generators or other custom scripts could go here
    # (e.g. docs updates)

    # Exit 0 only if we fixed something and the healthcheck passes
    if fixed and pass_health():
        sys.exit(0)
    else:
        # Either we didn't fix anything, or the healthcheck still fails
        sys.exit(1)

if __name__ == "__main__":
    main()
