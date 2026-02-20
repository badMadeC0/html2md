"""Export html2md JSONL logs to CSV."""

import argparse
import csv
import json
from pathlib import Path


def _sanitize_csv_cell(value: object) -> object:
    """Prevent spreadsheet formula execution for string values."""
    if isinstance(value, str) and value.startswith(('=', '+', '-', '@')):
        return f"'{value}"
    return value


def _build_unique_output_fields(fields: list[str]) -> list[str]:
def _build_unique_output_fields(fields: list[str]) -> list[str]:
    """Return sanitized output headers while preserving one column per requested field."""
    output_fields: list[str] = []
    used_names: set[str] = set()

    for field in fields:
        base_name = str(_sanitize_csv_cell(field))
        candidate = base_name
        count = 1
        while candidate in used_names:
            candidate = f"{base_name}_{count}"
            count += 1
        used_names.add(candidate)
        output_fields.append(candidate)

    return output_fields

def main(argv=None):
    """Run the log export CLI."""
    ap = argparse.ArgumentParser(
        prog='html2md-log-export', description='Export html2md JSONL logs to CSV'
    )
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--fields', default='ts,input,output,status,reason')
    args = ap.parse_args(argv)
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    output_fields = _build_unique_output_fields(fields)

    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=output_fields, restval='', extrasaction='ignore')
        w.writeheader()
        for line in fi:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            row = {
                output_key: (
                    '' if (value := rec.get(input_key)) is None
                    else _sanitize_csv_cell(value)
                ) for input_key, output_key in zip(fields, output_fields)
            }
            w.writerow(row)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
