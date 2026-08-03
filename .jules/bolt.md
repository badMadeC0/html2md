# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop (Updated)

**Learning:** When optimizing Python hot loops, string allocations (like `lstrip()`) are incredibly expensive compared to simple property checks or boolean evaluations. A check like `value[0].isspace()` correctly handles Unicode whitespace identically to `lstrip()` but executes in O(1) time without allocating memory. When short-circuiting logic to avoid string allocations, do not alter type-checks (`isinstance`) to exact checks (`type() is`), as this breaks polymorphism for subclasses and constitutes an anti-pattern. Also, keep performance scratchpads out of the main repository.

**Action:** Add fast-path short-circuits (`isspace()`, etc) before expensive string transformations. Avoid changing `isinstance` checks unless specifically fixing a bug related to exact types. Always clean up performance measurement scripts before committing.
