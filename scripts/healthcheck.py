import subprocess
import sys

def main():
    print("Running tests...")
    result = subprocess.run(["pytest", "-q"])
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()
