#!/usr/bin/env python3
import subprocess
import sys
import os


def run_command(command, description, ignore_failure=False):
    print(f"\n==> {description}")
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"FAILED: {description}")
        if not ignore_failure:
            return False
        return True


def main():
    print("Attempting self-heal repairs...")

    # 1. Install dependencies (best effort, mainly for CI)
    # Using python -m pip to ensure we use the same python environment
    run_command(
        f"{sys.executable} -m pip install -e .[dev]",
        "Install dependencies",
        ignore_failure=True,
    )

    # 2. Fix formatting
    run_command("black .", "Fix formatting (black)", ignore_failure=True)

    # 3. Verify health
    print("\nVerifying health after repairs...")
    # Get path to healthcheck script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    healthcheck_script = os.path.join(script_dir, "healthcheck.py")

    try:
        subprocess.run([sys.executable, healthcheck_script], check=True)
        print("\nSelf-heal successful!")
        sys.exit(0)
    except subprocess.CalledProcessError:
        print("\nSelf-heal failed: Healthcheck still failing.")
        sys.exit(1)


if __name__ == "__main__":
    main()
