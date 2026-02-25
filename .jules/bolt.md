## 2024-05-24 - Python String Optimizations
**Learning:** `str.strip()` allocates a new string, which is expensive in tight loops (e.g. parsing large files). `str.isspace()` is significantly faster for checking whitespace-only lines without allocation. `json.loads()` handles surrounding whitespace correctly, making `strip()` redundant for valid JSON lines.
**Action:** In tight loops parsing text, prefer `isspace()` or direct parsing over `strip()` if only checking for empty/whitespace lines.

## 2024-05-25 - Python String Prefix Checks
**Learning:** When sanitizing strings in tight loops (e.g., millions of log entries), `str.lstrip().startswith(...)` creates unnecessary string copies for safe strings. Checking `value[0]` against a set of dangerous prefixes and whitespace is ~20% faster for the common case (safe strings).
**Action:** Use a fast-path check (e.g., `value[0] not in DANGEROUS and not value[0].isspace()`) before falling back to expensive string manipulations like `lstrip()` for sanitization.
