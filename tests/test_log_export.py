"""Tests for the log export functionality."""
import json
import csv
from pathlib import Path
from html2md.log_export import main

def test_log_export_success(tmp_path: Path):
    """Verify log export succeeds and writes expected CSV rows/headers."""
    # Setup test input
    inp = tmp_path / "input.jsonl"
    out = tmp_path / "output.csv"

    records = [
        {"ts": 1.1, "input": "http://a.com", "output": "a.md", "status": "ok", "reason": ""},
        {"ts": 1.2, "input": "http://b.com",
         "output": "b.md", "status": "fail", "reason": "404", "extra": "ignored"}
    ]

    with open(inp, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
        f.write("\n") # Empty line should be skipped
        f.write("   \n") # Whitespace line should be skipped
        f.write("invalid json line\n") # Should be skipped

    # Run the function
    exit_code = main(["--in", str(inp), "--out", str(out)])
    assert exit_code == 0

    # Verify output
    assert out.exists()
    with open(out, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["input"] == "http://a.com"
    assert rows[0]["status"] == "ok"
    assert rows[1]["input"] == "http://b.com"
    assert "extra" not in rows[0] # Verify header only contains requested fields

def test_log_export_missing_fields(tmp_path: Path):
    """Verify missing fields are exported as empty strings."""
    inp = tmp_path / "input_missing.jsonl"
    out = tmp_path / "output_missing.csv"

    records = [
        {"ts": 1.1, "input": "http://a.com"} # Missing other fields
    ]

    with open(inp, "w", encoding="utf-8") as f:
        f.write(json.dumps(records[0]) + "\n")

    exit_code = main(["--in", str(inp), "--out", str(out)])
    assert exit_code == 0

    with open(out, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1

    assert rows[0]["status"] == "" # Default empty string for missing fields
