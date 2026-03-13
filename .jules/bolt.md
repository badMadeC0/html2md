## 2024-05-24 - [Optimize CSV export bottleneck]
**Learning:** `str.lstrip()` creates a new string allocation and is slow when executed millions of times in a hot loop (like CSV exporting where every field of every row is sanitized).
**Action:** When guarding against characters that might be preceded by whitespace, do a cheap `str[0].isspace()` check first before invoking `lstrip()`.
