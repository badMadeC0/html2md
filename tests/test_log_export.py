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


def test_log_export_null_becomes_empty_string(tmp_path):
    """Test explicit null values are exported as empty strings."""
    input_file = tmp_path / "nulls.jsonl"
    output_file = tmp_path / "nulls.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"ts": "1", "status": null}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'ts,status']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['ts'] == "1"
        assert rows[0]['status'] == ""


def test_log_export_sanitizes_csv_formulas(tmp_path):
    """Test formula-like headers and values are escaped for CSV safety."""
    input_file = tmp_path / "formulas.jsonl"
    output_file = tmp_path / "formulas.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"safe": "=1+1", "@bad": "@SUM(A1:A2)"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'safe,@bad']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert reader.fieldnames == ['safe', "'@bad"]
        assert rows[0]['safe'] == "'=1+1"
        assert rows[0]["'@bad"] == "'@SUM(A1:A2)"


def test_log_export_preserves_distinct_fields_when_sanitized_headers_collide(tmp_path):
    """Distinct requested fields should remain distinct after header sanitization."""
    input_file = tmp_path / "colliding_headers.jsonl"
    output_file = tmp_path / "colliding_headers.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"@a": "formula", "\'@a": "literal"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', "@a,'@a"]
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert reader.fieldnames == ["'@a", "'@a_1"]
        assert rows[0]["'@a"] == "formula"
        assert rows[0]["'@a_1"] == "literal"


def test_log_export_handles_generated_suffix_name_collision(tmp_path):
    """Repeated fields stay unique even when one already has a numeric suffix."""
    input_file = tmp_path / "suffix_collision.jsonl"
    output_file = tmp_path / "suffix_collision.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"a": "v1", "a_1": "v2"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'a,a_1,a']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert reader.fieldnames == ["a", "a_1", "a_2"]
        assert rows[0]["a"] == "v1"
        assert rows[0]["a_1"] == "v2"
        assert rows[0]["a_2"] == "v1"


def test_log_export_sanitizes_leading_whitespace_formula(tmp_path):
    """Values with leading whitespace before formulas are escaped."""
    input_file = tmp_path / "leading_whitespace_formula.jsonl"
    output_file = tmp_path / "leading_whitespace_formula.csv"

    with open(input_file, "w", encoding="utf-8") as f:
        f.write('{"safe": "\\t=1+1"}\n')

    argv = ['--in', str(input_file), '--out', str(output_file), '--fields', 'safe']
    main(argv)

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]['safe'] == "'\t=1+1"
