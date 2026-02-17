
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
    print(f"DEBUG: Processing {inp} to {out}")
    print(f"DEBUG: Fields: {fields}")

    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        # Optimized: Use csv.writer with direct list comprehension instead of DictWriter.
        # This avoids DictWriter's method call overhead and internal dictionary lookups per row.
        # In local testing this provided a modest throughput improvement; actual gains may vary by environment.
        w = csv.writer(fo)
        w.writerow(fields)
        count = 0
        for line in fi:
            # Optimized: Avoid string allocation from strip() for empty check
            if line.isspace(): continue
            try: rec=json.loads(line)
            except json.JSONDecodeError: continue
            w.writerow([rec.get(f, '') for f in fields])
            count += 1
        print(f"DEBUG: Processed {count} records")
    return 0

if __name__=='__main__':
    raise SystemExit(main())
