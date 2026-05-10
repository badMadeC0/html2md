## 2026-05-10 - Fast-path character checks
**Learning:** Checking a single character against a string (`char in "=+-@"`) is much faster than checking against a tuple (`char in ("=", "+", "-", "@")`). Also, caching indexed characters (like `value[0]`) in tight loops like `_sanitize_formula` avoids redundant lookup overheads and saves measurable time when running over thousands of elements.
**Action:** Use strings for checking single characters instead of tuples when possible, and cache indexed lookups when used repeatedly.
