"""Security tests for CSV export."""

import csv
import json
from html2md.log_export import main

def test_log_export_csv_injection(tmp_path):
    """Test that potential CSV injection payloads are sanitized."""
    input_file = tmp_path / "injection.jsonl"
    output_file = tmp_path / "injection.csv"

    # Malicious payloads targeting Excel/Sheets
    payloads = [
        {"ts": "1", "input": "=SUM(1,2)", "status": "ok"},
        {"ts": "2", "input": "+SUM(1,2)", "status": "ok"},
        {"ts": "3", "input": "-SUM(1,2)", "status": "ok"},
        {"ts": "4", "input": "@SUM(1,2)", "status": "ok"},
        {"ts": "5", "input": "safe_value", "status": "ok"},
    ]

    with open(input_file, "w", encoding="utf-8") as f:
        for item in payloads:
            f.write(json.dumps(item) + "\n")

    argv = [
        '--in', str(input_file),
        '--out', str(output_file),
        '--fields', 'ts,input,status'
    ]

    ret = main(argv)
    assert ret == 0

    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

        # Verify row count
        assert len(rows) == 5

        # Check sanitization (expect leading single quote)
        assert rows[0]['input'] == "'=SUM(1,2)"
        assert rows[1]['input'] == "'+SUM(1,2)"
        assert rows[2]['input'] == "'-SUM(1,2)"
        assert rows[3]['input'] == "'@SUM(1,2)"
        assert rows[4]['input'] == "safe_value"
