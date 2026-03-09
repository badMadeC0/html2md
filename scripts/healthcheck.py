import subprocess
import sys

def run_cmd(cmd):
    print(f"==> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(1)

def main():
    run_cmd("pytest -q")
    run_cmd("black --check src tests")

if __name__ == "__main__":
    main()
