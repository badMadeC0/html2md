## 2024-05-22 - [Optimizing CSV Export]
**Learning:** `csv.DictWriter` with `extrasaction='ignore'` avoids creating intermediate dictionaries in Python loops, yielding ~16% speedup.
**Action:** Use `extrasaction='ignore'` and `restval=''` instead of dictionary comprehensions for high-volume CSV writing.
