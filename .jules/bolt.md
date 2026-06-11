# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-06-11 - Avoid Expensive `lstrip()` Calls in String Sanitization Hot Loop
**Learning:** During log export processing (`src/html2md/log_export.py`), `value.lstrip()` was being called on every string to check for leading dangerous prefixes even if the string wasn't whitespace-padded. `str.lstrip()` allocates a new string in memory. By guarding `value.lstrip().startswith(...)` with an `isspace()` check on the first character `c`, we avoided this allocation for normal text, achieving a ~1.6x speedup (2.6s vs 4.1s in bench) and reducing memory pressure significantly for typical large datasets.
**Action:** When performing string sanitization or parsing in hot loops, always add guards before methods that allocate new strings (like `lstrip`, `strip`, `replace`).
