## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2025-02-28 - CSV Sanitization Fast Path String Allocation Bypass

**Learning:** Optimizing a string validation algorithm in `log_export.py` using `first_char.isspace()` yielded a ~15% performance improvement on the hot loop. The key insight was that `value.lstrip().startswith(...)` creates a new string object *every single time* for any string that doesn't start with an explicit dangerous character (e.g., standard words like "hello" or "value"), even if there is no leading whitespace to strip. By first checking if `value[0]` is a space (a fast boolean check) before doing the `lstrip()`, we avoid the string allocation overhead for the >99% typical case where there is no leading whitespace.
**Action:** When validating string prefixes in high-volume processing loops, avoid operations that allocate new strings (`lstrip()`, `rstrip()`, `replace()`, etc.) unless a fast-path condition (like `isspace()`) proves the allocation is necessary.
