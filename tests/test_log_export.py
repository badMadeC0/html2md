
import json
import csv
from html2md.log_export import main

def test_main_happy_path(tmp_path):
    log_file = tmp_path / "logs.jsonl"
    csv_file = tmp_path / "out.csv"

    data = [
        {"ts": "2023-01-01T00:00:00", "input": "http://example.com", "output": "example.md", "status": "ok", "reason": ""},
        {"ts": "2023-01-01T00:00:01", "input": "http://example.org", "output": "example_org.md", "status": "error", "reason": "404"},
    ]

    with log_file.open("w", encoding="utf-8") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")

    argv = ["--in", str(log_file), "--out", str(csv_file)]
    ret = main(argv)

    assert ret == 0
    assert csv_file.exists()

    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["ts"] == "2023-01-01T00:00:00"
    assert rows[1]["reason"] == "404"

def test_main_empty_input(tmp_path):
    log_file = tmp_path / "empty.jsonl"
    csv_file = tmp_path / "out.csv"

    log_file.write_text("")

    argv = ["--in", str(log_file), "--out", str(csv_file)]
    ret = main(argv)

    assert ret == 0
    assert csv_file.exists()

    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 0

def test_main_invalid_json_lines(tmp_path):
    log_file = tmp_path / "invalid.jsonl"
    csv_file = tmp_path / "out.csv"

    with log_file.open("w", encoding="utf-8") as f:
        f.write('{"ts": "ok"}\n')
        f.write('invalid json\n')
        f.write('\n')
        f.write('{"ts": "ok2"}\n')

    argv = ["--in", str(log_file), "--out", str(csv_file), "--fields", "ts"]
    ret = main(argv)

    assert ret == 0

    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["ts"] == "ok"
    assert rows[1]["ts"] == "ok2"

def test_main_custom_fields(tmp_path):
    log_file = tmp_path / "logs.jsonl"
    csv_file = tmp_path / "out.csv"

    entry = {"ts": "2023", "input": "in", "output": "out", "extra": "val"}
    log_file.write_text(json.dumps(entry) + "\n")

    argv = ["--in", str(log_file), "--out", str(csv_file), "--fields", "ts,extra"]
    ret = main(argv)

    assert ret == 0

    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ["ts", "extra"]
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["ts"] == "2023"
    assert rows[0]["extra"] == "val"
    assert "input" not in rows[0]
