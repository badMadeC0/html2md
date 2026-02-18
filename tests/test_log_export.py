import json
import csv
from pathlib import Path
from html2md.log_export import main

def test_csv_injection(tmp_path):
    infile = tmp_path / "test.jsonl"
    outfile = tmp_path / "test.csv"

    data = {"ts": "2023-01-01", "input": "=1+1", "output": "+cmd", "status": "-risk", "reason": "@sum"}
    with open(infile, "w", encoding="utf-8") as f:
        json.dump(data, f)
        f.write("\n")

    argv = ["--in", str(infile), "--out", str(outfile)]
    assert main(argv) == 0

    with open(outfile, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        row = next(reader)

    # Verify values are prepended with a single quote
    assert row["input"] == "'=1+1"
    assert row["output"] == "'+cmd"
    assert row["status"] == "'-risk"
    assert row["reason"] == "'@sum"
