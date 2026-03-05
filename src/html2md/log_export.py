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
        prog="html2md-log-export", description="Export html2md JSONL logs to CSV"
    )
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", dest="out", required=True)
    ap.add_argument("--fields", default="ts,input,output,status,reason")
    args = ap.parse_args(argv)

    fields = [f.strip() for f in args.fields.split(",") if f.strip()]
    fieldnames, mapping = _unique_fieldnames(fields)

    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open("r", encoding="utf-8") as fi, out.open(
        "w", newline="", encoding="utf-8"
    ) as fo:
        w = csv.DictWriter(fo, fieldnames=fieldnames, extrasaction="ignore", restval="")
        w.writeheader()

        # Pre-compute to avoid global lookup overhead in the loop
        loads = json.loads
        dangerous_prefixes = _DANGEROUS_PREFIXES

        for line in fi:
            if not line.strip():
                continue

            try:
                rec = loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(rec, dict):
                continue

            # Optimize per-row processing: csv.DictWriter natively ignores
            # extra keys via extrasaction='ignore' and handles missing keys
            # via restval=''
            row = {}
            for input_name, output_name in mapping:
                val = rec.get(input_name)
                if val is not None:
                    if type(val) is str:
                        if not val.startswith("'"):
                            l = val.lstrip()
                            if l and l.startswith(dangerous_prefixes):
                                row[output_name] = f"'{val}"
                                continue
                    row[output_name] = val

            w.writerow(row)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
