#!/usr/bin/env python3
import subprocess
import sys


def run_command(command, description):
    print(f"\n==> {description}")
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"FAILED: {description}")
        return False


def main():
    checks = [
        ("black --check .", "Check formatting (black)"),
        ("pytest -q", "Run tests (pytest)"),
    ]

    failed = False
    for cmd, desc in checks:
        if not run_command(cmd, desc):
            failed = True

    if failed:
        sys.exit(1)

    print("\nHealthcheck passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
