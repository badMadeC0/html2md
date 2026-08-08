# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-24 - Further Python Fast Path Optimizations for CSV/JSON Export Loop
**Learning:** We can squeeze out additional performance improvements in the string sanitization path (preventing CSV injections). Rather than running `.lstrip().startswith(...)` for all strings, it is faster to extract the first character and check it against a `set` for exact match prefixes (`=`, `+`, `-`, `@`), and only perform `.lstrip().startswith()` (against a `tuple`) if the first character is whitespace. In addition, replacing `isinstance` with `type() is` in the `_sanitize_value` logic reduces function call overhead.
**Action:** When evaluating strings against a small set of dangerous prefixes in a hot loop, checking the first character against a `set` and avoiding `.lstrip` unless necessary yields measurable performance improvements. Also prefer `type() is` when inheritance is not a concern for strict dictionary checks.
