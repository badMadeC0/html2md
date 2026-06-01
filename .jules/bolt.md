# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Python Fast Path String Sanitization Optimization

**Learning:** When sanitizing strings in a hot loop (like a JSONL to CSV converter), string allocations (like `lstrip()`) are a significant source of overhead.

In `_sanitize_formula`, we originally had:
`if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):`

This was calling `.lstrip()` and allocating a new string for almost every single value being processed, even if it didn't start with whitespace.

By changing this to first check if the string actually starts with whitespace using `.isspace()`, we can completely skip the `lstrip()` operation and allocation for the vast majority of standard strings:
`if first_char.isspace() and value.lstrip().startswith(_DANGEROUS_PREFIXES):`

Furthermore, `type(val) is X` is significantly faster than `isinstance(val, X)` in hot loops when you are certain subclass checking is not required (e.g., standard dicts and strings in basic JSON serialization). Finally, using a `set` for character lookups is faster than a `tuple`.

**Action:**
- Use `if str[0].isspace():` to guard expensive `.lstrip()` or `.strip()` calls if the goal is only to handle cases where leading whitespace is present.
- Use `type(x) is y` instead of `isinstance(x, y)` in serialization hot loops where strict types are expected.
- Use a `set` for membership testing (`in`) even for small collections of strings if checked in a hot loop.
