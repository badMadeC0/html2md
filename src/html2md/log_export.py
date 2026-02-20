"""Export html2md JSONL logs to CSV."""

import argparse
import json
import csv
from pathlib import Path


def main(argv=None):
    """Run the log export CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md-log-export", description="Export html2md JSONL logs to CSV"
    )
    ap.add_argument("--input", dest="inp", required=True)
    ap.add_argument("--output", dest="out", required=True)
    ap.add_argument("--fields", default="ts,input,output,status,reason")
    args = ap.parse_args(argv)
    fields = [f.strip() for f in args.fields.split(",") if f.strip()]
    inp = Path(args.inp)
    out = Path(args.out)

    with inp.open("r", encoding="utf-8") as fi, out.open(
        "w", newline="", encoding="utf-8"
    ) as fo:
        writer = csv.writer(fo)
        writer.writerow(fields)

        # Optimize: Pre-bind methods for faster loop execution
        writerow = writer.writerow
        json_loads = json.loads

        for line in fi:
            # Optimize: Avoid string allocation with strip()
            if line.isspace():
                continue
            try:
                rec = json_loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue

            # Sanitize fields to prevent CSV injection
            for key in fields:
                value = rec.get(key)
                if isinstance(value, str) and value.startswith(('=', '+', '-', '@', '\t', '\r')):
                    rec[key] = "'" + value

            w.writerow(rec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
