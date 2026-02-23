"""Export html2md JSONL logs to CSV."""

import argparse
import csv
import json
from pathlib import Path

_FORMULA_PREFIXES = ('=', '+', '-', '@')
_CONTROL_PREFIXES = ('\t', '\r')


def sanitize_csv_field(value):
    """Sanitize a field to prevent CSV injection."""
    if isinstance(value, str):
        # Check for formula injection (stripping all whitespace)
        if value.lstrip().startswith(_FORMULA_PREFIXES):
            return f"'{value}"
        # Check for control character injection (stripping only spaces to detect \t, \r)
        if value.lstrip(" ").startswith(_CONTROL_PREFIXES):
            return f"'{value}"
    return value


def _unique_fieldnames(fields: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Return deduplicated/sanitized CSV headers and original->output mapping."""
    used: set[str] = set()
    out_fields: list[str] = []
    mapping: list[tuple[str, str]] = []

    for field in fields:
        base = sanitize_csv_field(field)
        if not isinstance(base, str):
             base = str(base)

        candidate = base
        suffix = 1
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1

        used.add(candidate)
        out_fields.append(candidate)
        mapping.append((field, candidate))

    return out_fields, mapping


def _sanitize_value(value: object) -> object:
    """Return CSV-safe value."""
    if value is None:
        return ""
    return sanitize_csv_field(value)


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
    fieldnames, mapping = _unique_fieldnames(fields)

    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=fieldnames, extrasaction='ignore', restval='')
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
                output_name: _sanitize_value(rec.get(input_name, ""))
                for input_name, output_name in mapping
            }
            w.writerow(row)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
