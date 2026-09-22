import subprocess
import sys

def changed():
    out = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    return len(out.stdout.strip()) > 0

def pass_health():
    try:
        subprocess.run([sys.executable, "scripts/healthcheck.py"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    fixed = False

    print("\n$ black .")
    try:
        subprocess.run(["black", "."], check=True)
    except subprocess.CalledProcessError:
        pass

    if pass_health():
        fixed = changed()

    if fixed:
        print("Self-heal successful.")
        sys.exit(0)
    else:
        print("Self-heal failed or no changes needed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
