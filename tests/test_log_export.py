"""Tests for log export functionality."""

import csv
import json

from html2md.log_export import main  # type: ignore


def test_log_export_basic(tmp_path):
    """Test basic log export."""
    input_file = tmp_path / "test.jsonl"
    output_file = tmp_path / "test.csv"

    data = [
        {"ts": "1", "input": "in1", "output": "out1", "status": "ok", "reason": ""},
        {"ts": "2", "input": "in2", "output": "out2", "status": "err", "reason": "fail"},
    ]

    with input_file.open("w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    argv = ["--in", str(input_file), "--out", str(output_file), "--fields", "ts,input,output,status,reason"]
    ret = main(argv)
    assert ret == 0

    with output_file.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["ts"] == "1"
        assert rows[1]["status"] == "err"


def test_log_export_malformed_and_non_dict_json(tmp_path):
    """Test handling of malformed JSON and valid non-dict JSON values."""
    input_file = tmp_path / "mixed.jsonl"
    output_file = tmp_path / "mixed.csv"

    with input_file.open("w", encoding="utf-8") as f:
        f.write('{"ts": "1"}\n')
        f.write("not valid json\n")
        f.write("[1, 2, 3]\n")
        f.write('"string"\n')
        f.write('{"ts": "2"}\n')

    argv = ["--in", str(input_file), "--out", str(output_file), "--fields", "ts"]
    main(argv)

    with output_file.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["ts"] == "1"
    assert rows[1]["ts"] == "2"


def test_log_export_extra_missing_fields(tmp_path):
    """Test handling of extra or missing fields."""
    input_file = tmp_path / "fields.jsonl"
    output_file = tmp_path / "fields.csv"

    data = [{"a": "1", "b": "2", "c": "3"}, {"a": "4"}]

    with input_file.open("w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item) + "\n")

    argv = ["--in", str(input_file), "--out", str(output_file), "--fields", "a,b"]
    main(argv)

    with output_file.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 2
    assert rows[0]["a"] == "1"
    assert rows[0]["b"] == "2"
    assert rows[1]["a"] == "4"
    assert rows[1]["b"] == ""
