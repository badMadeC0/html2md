## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-03-24 - [Optimize CSV sanitization and dict lookups in log_export.py]
**Learning:** Python string `.lstrip()` is relatively expensive when run millions of times in a hot loop. By checking if the first character is whitespace (e.g., `value[0].isspace()`) before invoking `.lstrip()`, we can provide a fast path for the vast majority of strings that do not start with whitespace, avoiding the expensive call. Additionally, pre-fetching methods like `dict.get` as local variables avoids dictionary attribute lookups in the inner loop, providing a measurable performance boost.
**Action:** When writing hot loops involving string manipulation, look for fast paths that avoid expensive string methods like `.lstrip()` or `.replace()`. Also, remember to pre-fetch common methods (like `dict.get`) outside of loops to avoid the overhead of Python's dynamic attribute lookup.
