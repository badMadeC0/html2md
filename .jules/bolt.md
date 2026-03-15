## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

## 2024-05-24 - Avoiding Unnecessary String Allocations in CSV Sanitization
**Learning:** Checking for space character `c.isspace()` as a short-circuit condition before using `value.lstrip().startswith(_DANGEROUS_PREFIXES)` avoids a string allocation (due to `lstrip()`) and function call for strings that do not start with space. In loops, this results in a significant throughput improvement (around ~38% faster for normal strings).
**Action:** When a string manipulation like `lstrip()` or `strip()` is conditionally needed to examine a prefix, perform a fast `c.isspace()` check (or `c in ' \t\n\r'`) on the first character to bypass the allocation for common strings.
