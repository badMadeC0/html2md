## 2024-05-22 - [Optimizing CSV Export]
**Learning:** `csv.DictWriter` with `extrasaction='ignore'` avoids creating intermediate dictionaries in Python loops, yielding ~16% speedup.
**Action:** Use `extrasaction='ignore'` and `restval=''` instead of dictionary comprehensions for high-volume CSV writing.

## 2024-02-16 - [Manual CSV Writing vs DictWriter]
**Learning:** `csv.writer` with manual list comprehension `[d.get(k, '') for k in fields]` is ~24% faster than `csv.DictWriter` because it avoids per-row method call overhead and internal dictionary lookups.
**Action:** For high-performance CSV export where fields are known, prefer `csv.writer` with manual field extraction over `csv.DictWriter`.
