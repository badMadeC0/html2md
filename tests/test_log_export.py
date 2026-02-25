
import json
import csv
from pathlib import Path
from html2md.log_export import main

def test_log_export(tmp_path):
    log_file = tmp_path / "test.jsonl"
    out_file = tmp_path / "test.csv"

    log_content = [
        {"ts": "2023-01-01 00:00:00", "input": "http://example.com", "output": "example.md", "status": "ok", "reason": ""},
        "invalid json",
        "[]",
        "null",
        "123",
        "\"string\"",
        {"ts": "2023-01-01 00:01:00", "input": "http://example.org", "output": "example_org.md", "status": "ok", "reason": ""}
    ]

    with log_file.open("w", encoding="utf-8") as f:
        for item in log_content:
            if isinstance(item, dict):
                f.write(json.dumps(item) + "\n")
            else:
                f.write(item + "\n")

    main(["--in", str(log_file), "--out", str(out_file)])

    assert out_file.exists()

    with out_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["input"] == "http://example.com"
    assert rows[1]["input"] == "http://example.org"
