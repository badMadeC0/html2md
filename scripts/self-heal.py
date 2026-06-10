import subprocess
import sys

def sh(cmd: str, ignore_error: bool = False):
    print(f"\n$ {cmd}")
    try:
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        if not ignore_error:
            pass
        return False

def pass_health():
    return sh("python scripts/healthcheck.py", ignore_error=True)

def changed():
    try:
        out = subprocess.check_output("git status --porcelain", shell=True, text=True)
        return len(out.strip()) > 0
    except subprocess.CalledProcessError:
        return False

def main():
    fixed = False

    # 1) Lint/format auto-fix
    sh("black src tests", ignore_error=True)
    health_passed = pass_health()
    if health_passed:
        fixed = fixed or changed()

    # If it fails, we return non-zero so we know we couldn't fix it fully
    if not health_passed:
        sys.exit(1)

    if not fixed:
        print("No changes were made or nothing to fix.")
        # If no changes but it passes health, that means it was already healthy.
        # But we still exit 0 to indicate success, workflow can check for PR diffs
        sys.exit(0)

    print("Self-heal successfully applied fixes.")
    sys.exit(0)

if __name__ == "__main__":
    main()
