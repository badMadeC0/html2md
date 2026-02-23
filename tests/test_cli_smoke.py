
import os
import subprocess
import sys


def run(args):
    env = os.environ.copy()
    env["PYTHONPATH"] = f"src{os.pathsep}{env.get('PYTHONPATH', '')}".rstrip(os.pathsep)
    return subprocess.run([sys.executable, *args], capture_output=True, text=True, env=env)


def test_help_runs():
    r = run(["-m", "html2md.cli", "--help"])
    assert r.returncode == 0, r.stderr


def test_log_export_help_runs():
    r = run(["-m", "html2md.log_export", "--help"])
    assert r.returncode == 0, r.stderr


def test_log_export_roundtrip(tmp_path):
    inp = tmp_path / "in.jsonl"
    out = tmp_path / "out.csv"
    inp.write_text(
        '{"ts":"1","input":"i1","output":"o1","status":"ok"}\n'
        '{"ts":"2","input":"i2","output":"o2","status":"ok","extra":"ignored"}\n'
        'not-json\n',
        encoding='utf-8',
    )

    r = run(["-m", "html2md.log_export", "--in", str(inp), "--out", str(out), "--fields", "ts,input,output,status,reason"])
    assert r.returncode == 0, r.stderr

    assert out.read_text(encoding='utf-8') == (
        "ts,input,output,status,reason\n"
        "1,i1,o1,ok,\n"
        "2,i2,o2,ok,\n"
    )
