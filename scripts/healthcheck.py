import subprocess
import sys


def run_check(name, cmd):
    print(f"\n==> {name}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"[healthcheck] {name} failed")
        return False
    return True


def main():
    success = True

    if not run_check("Formatting (black)", "black --fast --check ."):
        success = False

    if not run_check("Tests (pytest)", "pytest -q"):
        success = False

    if not success:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
