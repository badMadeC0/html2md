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
            if not isinstance(rec, dict):
                continue

            row = [_sanitize_value(rec.get(name, "")) for name in input_names]
            w.writerow(row)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
