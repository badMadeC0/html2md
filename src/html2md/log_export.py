
import argparse, json, csv
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
        w = csv.DictWriter(fo, fieldnames=fields, restval='', extrasaction='ignore'); w.writeheader()
        for line in fi:
            line=line.strip();
            if not line: continue
            try: rec=json.loads(line)
            except ValueError: continue
            # Build a row dict limited to the desired fields, normalizing None to '' to
            # preserve the original behavior for explicit null values in the JSON.
            row = {k: ('' if rec.get(k) is None else rec.get(k, '')) for k in fields}
            w.writerow(row)
    return 0

if __name__=='__main__':
    raise SystemExit(main())
