import subprocess
import sys


def sh(cmd):
    print(f"\n$ {cmd}")
    subprocess.run(cmd, shell=True, check=True)


def try_sh(cmd):
    try:
        sh(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def changed():
    try:
        out = subprocess.check_output("git status --porcelain", shell=True, text=True)
        return len(out.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def pass_health():
    return try_sh("python scripts/healthcheck.py")


def main():
    fixed = False

    # 1) Lint/format auto-fix
    try_sh("black --fast .")

    if pass_health():
        fixed = fixed or changed()

    # 2) Future self-healing operations can go here
    # e.g., missing typing additions, updating lockfile, etc.

    if fixed and pass_health():
        print("\nSelf-healing successful! Fixes generated.")
        sys.exit(0)
    else:
        print(
            "\nSelf-healing did not result in passing healthchecks or no fixes were generated."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
