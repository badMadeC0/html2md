# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-11-21 - Optimize Duplicate Column Sanitization with Hash Map
**Learning:** Found a performance bottleneck in `_unique_fieldnames` where duplicate field handling used an `O(N^2)` while loop `while candidate in used` over a set. For many duplicate fields, this was very slow. Replacing the `set` with a `dict` to store the next expected suffix (e.g., `used[base] = suffix + 1`) turned this into an `O(N)` hash map lookup, yielding a ~13x speedup on benchmarks with many duplicate elements (from ~3.2s to ~0.24s).
**Action:** When deduplicating strings with numerical suffixes, use a dictionary to keep track of the current maximum suffix for each base string to avoid quadratic collisions, instead of linearly checking `base_1`, `base_2`, etc. against a set.
