"""Export html2md JSONL logs to CSV."""

from __future__ import annotations
import argparse
import json
import csv
from pathlib import Path


def main(argv=None):
    """Parse arguments and export a JSONL log file to CSV format."""
    ap = argparse.ArgumentParser(
        prog='html2md-log-export', description='Export html2md JSONL logs to CSV'
    )
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--fields', default='ts,input,output,status,reason')
    args = ap.parse_args(argv)
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        w = csv.DictWriter(fo, fieldnames=fields, restval='', extrasaction='ignore')
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
            row = {k: ('' if rec.get(k) is None else rec.get(k, '')) for k in fields}
            w.writerow(row)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
