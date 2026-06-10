import subprocess
import sys

def run_cmd(cmd: str, name: str):
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, check=True, shell=True)
    except subprocess.CalledProcessError:
        print(f"[healthcheck] {name} failed")
        sys.exit(1)

def main():
    print("Running healthcheck...")
    run_cmd("black --check src tests", "Formatting Check (black)")
    run_cmd("pytest -q", "Unit Tests (pytest)")
    print("Healthcheck passed!")

if __name__ == "__main__":
    main()
