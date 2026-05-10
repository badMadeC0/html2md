#!/usr/bin/env python
"""
Minimal healthcheck for a Python repository.
Runs the same unit test gate as the ci workflow.
"""
import subprocess
import sys
import os

def run_cmd(name, cmd):
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[{name}] failed")
        sys.exit(1)

def main():
    # Setup PYTHONPATH
    os.environ['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')

    # Pytest check
    run_cmd("Unit tests", "pytest -q")

    print("\nAll healthchecks passed!")
    sys.exit(0)

if __name__ == "__main__":
    main()
