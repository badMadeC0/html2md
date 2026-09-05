# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop - Function Call Inlining

**Learning:** When optimizing tight inner loops in Python that process thousands of items (e.g. converting a large JSONL file to CSV), function call overhead becomes a bottleneck. In our previous optimization, replacing list unpacking and using native parsers provided a 40% gain. Further profiling showed that calling `sanitize(rec.get(name, ""))` for every single cell added notable overhead due to the repeated function call frame creation.
By replacing the list comprehension `[sanitize(...) for ...]` with a simple `for` loop, we were able to **inline** the sanitization logic (`_sanitize_value` and `_sanitize_formula`), completely eliminating function calls in the hot path.
Additionally, using `type(rec) is not dict` instead of `not isinstance(rec, dict)` and pre-casting the field names iteration sequence to a `tuple` provided micro-optimizations. These changes yielded another ~7-10% performance improvement on the inner loop execution time.

**Action:** When working on extremely hot data processing loops, consider manually inlining small helper functions into the loop body, as Python's function call overhead can dominate execution time. Also, `type(x) is T` is faster than `isinstance` for built-in exact type checks where polymorphism isn't needed.
