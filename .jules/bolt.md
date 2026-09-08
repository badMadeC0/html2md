# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

# 2024-09-08 - Python Fast Path Optimizations for CSV/JSON Export Loop - Avoid String Allocations

**Learning:** Optimizing `_sanitize_formula` in `log_export.py`. The original code called `.lstrip()` on every string that didn't immediately start with a dangerous prefix to catch things like `" =formula"`. In Python, `.lstrip()` allocates and returns a completely new string object. We can check if the first character is a space using `value[0].isspace()` before calling `.lstrip()`. This bypasses expensive string allocation for the vast majority of normal strings, yielding roughly a ~30% throughput increase for the function in benchmarks.
**Action:** When doing string manipulations in a hot loop (like `.lstrip()`, `.replace()`), use fast character checks (like `char.isspace()`, `char == "X"`) to avoid allocating new strings when the operation is unnecessary.
