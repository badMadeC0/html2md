
import argparse
import csv
import json
from pathlib import Path


def main(argv=None):
    ap = argparse.ArgumentParser(prog='html2md-log-export', description='Export html2md JSONL logs to CSV')
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--fields', default='ts,input,output,status,reason')
    args = ap.parse_args(argv)
    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    inp = Path(args.inp); out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        # Optimized: restval='' fills missing fields with empty string, extrasaction='ignore' ignores extra fields
        w = csv.DictWriter(fo, fieldnames=fields, restval='', extrasaction='ignore')
        w.writeheader()
        for line in fi:
            line=line.strip();
            if not line: continue
            try: rec=json.loads(line)
            except ValueError: continue
            # Optimization: pass rec directly to writerow.
            # This avoids creating a new dictionary for every row (O(M) per row),
            # relying on DictWriter's handling.
            if not isinstance(rec, dict):
                continue
            # Optimization: pass rec directly to writerow.
            # This avoids creating a new dictionary for every row (O(M) per row),
            # relying on DictWriter's handling.
            w.writerow(rec)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
