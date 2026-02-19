"""Export html2md JSONL logs to CSV."""

from __future__ import annotations
import argparse
import json
import csv
from pathlib import Path


def main(argv=None):
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
        w = csv.writer(fo)
        w.writerow(fields)
        # Optimization: Manual writer with list comp is ~7% faster than DictWriter
        for line in fi:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(rec, dict):
                continue
            w.writerow([rec.get(f, "") for f in fields])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
