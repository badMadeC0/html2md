## 2024-05-04 - [Optimize CSV Injection Sanitizer]
**Learning:** Checking `value[0].isspace()` is significantly faster than unconditionally calling `value.lstrip()` for string sanitization, as it avoids unnecessary string allocation for the >99% of strings that do not have leading whitespace.
**Action:** When inspecting hot paths that involve `.strip()` or `.lstrip()`, check if the string can be quickly evaluated first (e.g., using indexing or `isspace()`) to avoid the allocation overhead on normal inputs.
