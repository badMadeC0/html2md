# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2024-05-24 - Python Fast Path Optimizations for String Operations

**Learning:** When performing string sanitization on hot paths (such as checking if a log field starts with a formula character), short-circuiting expensive operations like `.lstrip()` makes a measurable difference. Previously, the code performed `value.lstrip().startswith(_DANGEROUS_PREFIXES)` on every string that didn't immediately start with a dangerous prefix, which resulted in a new string allocation for the vast majority of normal strings. Adding a simple `value[0].isspace()` check before calling `.lstrip()` entirely avoided this allocation for normal text fields.

Also learned that while replacing `isinstance(value, type)` with `type(value) is type` yields a very small performance boost by skipping the MRO check, it breaks polymorphism and is considered an anti-pattern in Python. It should be avoided unless absolutely critical and documented, as it caused a code review rejection.

**Action:** Before performing string allocation operations like `.lstrip()` in a tight loop, look for fast `O(1)` checks (like `.isspace()` on the first character) that can act as a gatekeeper to prevent the allocation entirely. Avoid replacing `isinstance` with `type() is` for micro-optimizations.
