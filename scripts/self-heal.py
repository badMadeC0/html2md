import subprocess
import sys

def main():
    print("Running auto-formatter (black)...")
    subprocess.run([sys.executable, "-m", "black", "."])

    print("Checking for changes...")
    status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)

    if status_result.stdout.strip():
        print("Changes detected. Running healthcheck...")
        healthcheck_result = subprocess.run([sys.executable, "scripts/healthcheck.py"])
        if healthcheck_result.returncode == 0:
            print("Healthcheck passed with repairs. Exiting with 0.")
            sys.exit(0)
        else:
            print("Healthcheck failed after repairs. Exiting with 1.")
            sys.exit(1)
    else:
        print("No changes made by auto-repairs. Exiting with 1.")
        sys.exit(1)

if __name__ == "__main__":
    main()
