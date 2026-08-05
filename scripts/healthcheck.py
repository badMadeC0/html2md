import sys
import subprocess
import os

def run_cmd(name, cmd):
    if not cmd:
        return
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"[healthcheck] {name} failed")
        sys.exit(1)

def main():
    try:
        # Run tests
        run_cmd("Unit tests", "pytest -q")

        # Run formatting check
        run_cmd("Formatting check", "black --check src tests")

        # We can add a simple build or additional static checks here if needed
        # e.g. run_cmd("Typecheck", "mypy src") if mypy was used

        sys.exit(0)
    except Exception as e:
        print(f"Healthcheck error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
