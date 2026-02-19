<<<<<<< bolt-optimize-log-export-7697383620298801973

import json
import csv
import tempfile
from pathlib import Path
from html2md.log_export import main

def test_log_export_main():
    with tempfile.TemporaryDirectory() as tmpdir:
        inp = Path(tmpdir) / 'input.jsonl'
        out = Path(tmpdir) / 'output.csv'

        # Test data covering various edge cases
        data = [
            {"ts": "2023-01-01", "input": "test", "output": "result", "status": "ok", "reason": ""},
            {"ts": "2023-01-02", "input": "missing_reason", "output": "result", "status": "ok"}, # missing field
            {"ts": "2023-01-03", "input": "extra_field", "output": "result", "status": "ok", "reason": "", "extra": "ignoreme"}, # extra field
            {"ts": "2023-01-04", "input": None, "output": "result", "status": "ok", "reason": ""}, # None value
            {"ts": "2023-01-05", "input": "", "output": "result", "status": "ok", "reason": "empty_string"}, # Empty string
        ]

        with inp.open('w', encoding='utf-8') as f:
            for d in data:
                f.write(json.dumps(d) + '\n')

        # Run main with arguments
        argv = ['--in', str(inp), '--out', str(out), '--fields', 'ts,input,output,status,reason']
        ret = main(argv)
        assert ret == 0

        # Verify output
        with out.open('r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            assert len(rows) == 5

            # Row 1: Standard
            assert rows[0]['ts'] == "2023-01-01"
            assert rows[0]['input'] == "test"

            # Row 2: Missing reason -> empty string
            assert rows[1]['ts'] == "2023-01-02"
            assert rows[1]['reason'] == ""

            # Row 3: Extra field -> ignored (not in CSV header/columns)
            assert rows[2]['ts'] == "2023-01-03"
            assert 'extra' not in rows[2]

            # Row 4: None value -> empty string (csv.DictWriter default for None)
            assert rows[3]['ts'] == "2023-01-04"
            assert rows[3]['input'] == ""

            # Row 5: Empty string -> empty string
            assert rows[4]['ts'] == "2023-01-05"
            assert rows[4]['input'] == ""
=======
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
>>>>>>> main
