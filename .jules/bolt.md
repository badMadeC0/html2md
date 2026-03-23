## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-24 - Further Fast Path Optimizations for CSV Formula Sanitization

**Learning:** When sanitizing strings for CSV export (to prevent formula injection), calling `value.lstrip().startswith(...)` for every value is surprisingly slow, even when the value doesn't start with a dangerous prefix, because `lstrip()` allocates a new string.
By first checking if the string starts with whitespace (`value[0].isspace()`) and only then calling `lstrip()`, we can achieve a ~2x speedup on typical data. Additionally, using `first in _DANGEROUS_PREFIXES` instead of `startswith(_DANGEROUS_PREFIXES)` on the first character avoids the overhead of checking a tuple of prefixes against multiple characters.

**Action:** When validating string prefixes in hot loops, avoid functions that allocate new strings like `lstrip()` unless absolutely necessary. Gate them behind fast character lookups like `value[0].isspace()`. Prefer exact character matching (`in`) over `startswith()` for single-character prefixes.
