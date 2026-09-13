#!/usr/bin/env python3
"""Minimal healthcheck for the html2md repo."""
import subprocess
import sys

def try_run(name: str, cmd: list[str]) -> None:
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError:
        print(f"[healthcheck] {name} failed")
        sys.exit(1)

def main() -> None:
    try_run("Unit tests", ["pytest", "-q"])
    print("Healthcheck passed.")

if __name__ == "__main__":
    main()
