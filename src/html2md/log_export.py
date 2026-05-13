"""Export html2md JSONL logs to CSV."""

import argparse
import csv
import json
from pathlib import Path

_DANGEROUS_STR = "=+-@"


def _sanitize_formula(value: str) -> str:
    """Prefix strings that look like formulas to prevent CSV injection."""
    # Fast path checks before expensive lstrip()
    if not value or value[0] == "'":
        return value

    if not value[0].isspace():
        if value[0] in _DANGEROUS_STR:
            return f"'{value}"
        return value

    stripped = value.lstrip()
    if stripped and stripped[0] in _DANGEROUS_STR:
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


def _sanitize_value(value: object) -> object:
    """Return CSV-safe value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return _sanitize_formula(value)
    return value


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
        # Optimization: Use csv.writer instead of DictWriter to avoid per-row dictionary overhead
        w = csv.writer(fo)
        w.writerow(fieldnames)

        # Hoist lookups out of hot loop for faster access (LOAD_FAST vs LOAD_GLOBAL/LOAD_ATTR)
        sanitize = _sanitize_value
        writerow = w.writerow
        loads = json.loads

        # Pre-extract names to avoid tuple unpacking in loop comprehension
        input_names = [name for name, _ in mapping]

        for line in fi:
            # json.loads ignores whitespace; skip manual strip/empty checks
            try:
                rec = loads(line)
            except json.JSONDecodeError:
                continue

            # Strict/fast dict check
            if not isinstance(rec, dict):
                continue

            writerow([
                sanitize(rec.get(name, ""))
                for name in input_names
            ])

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
