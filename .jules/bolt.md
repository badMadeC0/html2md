## 2024-05-22 - [Python CSV Performance: Manual Writer vs DictWriter]
**Learning:** `csv.DictWriter` adds significant overhead (~7% in this case) due to internal dictionary lookups and `extrasaction`/`restval` handling for every row.
**Action:** For high-throughput CSV writing where fields are known, use `csv.writer` with manual list comprehension (e.g., `[rec.get(f, '') for f in fields]`) to bypass the overhead.
