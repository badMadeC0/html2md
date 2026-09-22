# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Inlining and Exact Type Checks in Hot Loops
**Learning:** We observed ~20-30% performance improvements in Python hot loops by doing two small changes:
1. Replacing `isinstance(x, cls)` with `type(x) is cls` when subclassing isn't a concern. `type() is` performs a direct pointer comparison and avoids the MRO traversal of `isinstance()`.
2. Manually inlining very short utility functions (like `_sanitize_value(value)` -> `_sanitize_formula(value)`) when invoked per-field on every single record. Python function call overhead is relatively high; combining them into a single local function reduces stack frames.
Additionally, using a string for character inclusion `value[0] in "=+-@"` is faster than a tuple `value[0] in ("=", "+", "-", "@")` for single character checks.
**Action:** When a Python script is dominated by a very tight processing loop (e.g., transforming records field by field), use `type() is` for type checking, inline simple helper functions to reduce call overhead, and use string character inclusion rather than tuple inclusion.
