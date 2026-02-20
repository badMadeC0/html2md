"""Tests for log export functionality."""

import json
import csv
from html2md.log_export import main  # type: ignore


def test_log_export_basic(tmp_path):
    """Test basic log export."""
    input_file = tmp_path / "test.jsonl"
    output_file = tmp_path / "test.csv"

    data = [
        {"ts": "1", "input": "in1", "output": "out1", "status": "ok", "reason": ""},
        {"ts": "2", "input": "in2", "output": "out2", "status": "err", "reason": "fail"}
    ]

    with open(input_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    argv = [
        '--in', str(input_file),
        '--out', str(output_file),
        '--fields', 'ts,input,output,status,reason'
    ]
    ret = main(argv)
    assert ret == 0

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['ts'] == "1"
        assert rows[1]['status'] == "err"

def test_log_export_malformed_json(tmp_path):
    """Test handling of malformed JSON lines."""
    input_file = tmp_path / "malformed.jsonl"
    output_file = tmp_path / "malformed.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"ts": "1"}\n')
        f.write('not valid json\n')
        f.write('{"ts": "2"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'ts']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['ts'] == "1"
        assert rows[1]['ts'] == "2"

def test_log_export_extra_missing_fields(tmp_path):
    """Test handling of extra or missing fields."""
    input_file = tmp_path / "fields.jsonl"
    output_file = tmp_path / "fields.csv"

    # First row has extra field, second row misses 'b'
    data = [
        {"a": "1", "b": "2", "c": "3"},
        {"a": "4"}
    ]

    with open(input_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'a,b']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['a'] == "1"
        assert rows[0]['b'] == "2"
        # 'c' should be ignored (not in reader fieldnames)

        assert rows[1]['a'] == "4"
        assert rows[1]['b'] == "" # default restval

def test_log_export_non_dict_json(tmp_path):
    """Test handling of valid JSON that is not a dictionary."""
    input_file = tmp_path / "nondict.jsonl"
    output_file = tmp_path / "nondict.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"ts": "1"}\n')
        f.write('[1, 2, 3]\n') # valid json but not a dict
        f.write('"string"\n') # valid json but not a dict
        f.write('{"ts": "2"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'ts']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]['ts'] == "1"
        assert rows[1]['ts'] == "2"

def test_log_export_csv_injection(tmp_path):
    """Test that CSV injection formulas are sanitized."""
    input_file = tmp_path / "injection.jsonl"
    output_file = tmp_path / "injection.csv"

    # Malicious payload: starts with =
    payload = "=1+1"
    data = [
        {"input": payload, "output": "@SUM(1,1)", "status": "+ok", "reason": "\t-fail"}
    ]

    with open(input_file, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'input,output,status,reason']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        row = rows[0]
        # Check if fields are sanitized
        # We expect them to be prepended with '
        assert row['input'].startswith("'")
        assert row['output'].startswith("'")
        assert row['status'].startswith("'")
        assert row['reason'].startswith("'")
