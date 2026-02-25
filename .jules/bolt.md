## 2024-05-24 - Python String Optimizations
**Learning:** `str.strip()` allocates a new string, which is expensive in tight loops (e.g. parsing large files). `str.isspace()` is significantly faster for checking whitespace-only lines without allocation. `json.loads()` handles surrounding whitespace correctly, making `strip()` redundant for valid JSON lines.
**Action:** In tight loops parsing text, prefer `isspace()` or direct parsing over `strip()` if only checking for empty/whitespace lines.
