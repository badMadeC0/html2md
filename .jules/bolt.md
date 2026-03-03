## 2024-05-18 - JSONL to CSV Export Optimization
**Learning:** `csv.DictWriter` combined with per-row dictionary construction has significant overhead compared to `csv.writer` with a list comprehension for processing large log files. Even though `DictWriter` is safer, in tight loops where we already validate and construct the mapping (e.g. `_sanitize_value(rec.get(input_name, ""))`), we can bypass dictionary allocations completely.
**Action:** Default to `csv.writer` and list comprehensions for high-volume data export when the input-to-output mapping is predefined and stable.
