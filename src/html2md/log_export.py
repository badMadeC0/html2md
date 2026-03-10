"""Export html2md JSONL logs to CSV."""

import argparse
import csv
import json
from pathlib import Path

_DANGEROUS_PREFIXES = ("=", "+", "-", "@")


def _sanitize_formula(value: str) -> str:
    """Prefix strings that look like formulas to prevent CSV injection."""
    if value.startswith("'"):
        return value
    if value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value


def _unique_fieldnames(fields: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Return deduplicated/sanitized CSV headers and original->output mapping."""
    used: set[str] = set()
    out_fields: list[str] = []
    mapping: list[tuple[str, str]] = []

    for field in fields:
        base = _sanitize_formula(field)
        candidate = base
        suffix = 1
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1

        used.add(candidate)
        out_fields.append(candidate)
        mapping.append((field, candidate))

    return out_fields, mapping


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

    # Pre-extract input names outside the loop
    input_names = [m[0] for m in mapping]

    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        # Optimization: Use csv.writer instead of DictWriter to avoid per-row dictionary overhead
        w = csv.writer(fo)
        w.writerow(fieldnames)

        # Localize functions for the hot loop
        loads = json.loads
        writerow = w.writerow

        for line in fi:
            line = line.strip()
            if not line:
                continue

            try:
                rec = loads(line)
            except json.JSONDecodeError:
                continue

            if type(rec) is not dict:
                continue

            # Inline string sanitization logic to avoid per-cell function call overhead
            row = []
            append = row.append
            for name in input_names:
                v = rec.get(name, "")
                if type(v) is str:
                    if v.startswith("'"):
                        append(v)
                    elif v.lstrip().startswith(_DANGEROUS_PREFIXES):
                        append(f"'{v}")
                    else:
                        append(v)
                elif v is None:
                    append("")
                else:
                    append(v)

            writerow(row)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
