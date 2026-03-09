import subprocess
import sys

def run_cmd(cmd):
    print(f"==> {cmd}")
    subprocess.run(cmd, shell=True)

def main():
    run_cmd("black src tests")

if __name__ == "__main__":
    main()
