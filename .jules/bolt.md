# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Avoid redundant string allocation in lstrip()

**Learning:** `str.lstrip()` creates a new string in memory if there is any whitespace to strip, but even if there isn't, the method call overhead and string scanning still occur. In a hot loop (like checking thousands of records in `log_export.py` for dangerous CSV formula prefixes with `value.lstrip().startswith(...)`), avoiding `lstrip()` when we know there's no leading whitespace provides a measurable speedup. We can short-circuit this by checking `value[0].isspace()` first, which is a fast, no-allocation check on a single character.

**Action:** When performing `str.lstrip()` inside hot loops, especially when the vast majority of strings do not have leading whitespace, consider adding a quick check like `if value and value[0].isspace():` to skip the allocation and overhead.
