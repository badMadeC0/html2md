## 2024-05-24 - [Avoid lstrip for CSV formula sanitization]
**Learning:** `value.lstrip().startswith(...)` allocates a new string which can be expensive in Python, especially for large values or when called millions of times in a CSV export loop.
**Action:** Use an inline character loop to check the first non-whitespace character instead of `lstrip()` to avoid string allocation overhead.
