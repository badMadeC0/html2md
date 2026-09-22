import subprocess
import sys

def main():
    print("\n==> Run Unit tests")
    try:
        subprocess.run(["pytest", "-q"], check=True)
    except subprocess.CalledProcessError:
        print("[healthcheck] tests failed")
        sys.exit(1)

    print("[healthcheck] tests passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
