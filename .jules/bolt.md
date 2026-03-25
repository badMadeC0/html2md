## 2024-05-20 - [CSV Export Optimization]
**Learning:** `value.lstrip()` creates a copy of the string (an O(N) operation) and was being called for every non-formula string when sanitizing CSV exports. Checking `value[0].isspace()` provides a fast path to avoid this expensive string copy for the vast majority of normal strings.
**Action:** Before performing expensive string transformations like `lstrip()` or `replace()` in hot loops, always check if the transformation is necessary using fast O(1) checks like `isspace()` or simple character lookups.
