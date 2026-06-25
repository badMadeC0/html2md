# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop - Part 2

**Learning:** When sanitizing strings for CSV injection, checking `value[0]` before calling `lstrip()` saves substantial overhead. A naive `value.lstrip().startswith(...)` allocates a new string even when no whitespace is present. Instead, checking `value[0] in PREFIXES` covers 99% of valid cases, and we only need to call `lstrip()` if `value[0].isspace()`. Also, `type(val) is str` is consistently faster than `isinstance(val, str)` in tight loops.

**Action:** Whenever applying string manipulations like `lstrip()` or `replace()` in a hot loop, see if you can guard the manipulation with a fast index check (e.g. `c = value[0]`). And prefer `type() is X` over `isinstance` for hot type checks when exact matches are expected.
