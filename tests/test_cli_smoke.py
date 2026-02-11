
import subprocess

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, shell=True)

def test_help_runs():
    r = run("html2md --help")
    assert r.returncode == 0, r.stderr
