
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
