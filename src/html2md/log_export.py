"""Module to export JSONL logs to CSV."""
import argparse
import csv
import json
from pathlib import Path

def main(argv=None):
    """Main entry point for log export."""
    ap = argparse.ArgumentParser(
        prog='html2md-log-export',
        description='Export html2md JSONL logs to CSV'
    )
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--fields', default='ts,input,output,status,reason')
    args = ap.parse_args(argv)
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        # Optimized: Use extrasaction='ignore' to let C-level DictWriter handle filtering
        # and avoid creating a new dictionary for each row in Python.
        w = csv.DictWriter(fo, fieldnames=fields, extrasaction='ignore', restval='')
        w.writeheader()
        for line in fi:
            # Optimized: Avoid string allocation from strip() for empty check
            if line.isspace():
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            w.writerow(rec)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
