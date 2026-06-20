# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2024-06-25 - Avoid `lstrip()` and `startswith()` for CSV Injection checks

**Learning:** When sanitizing a large stream of log strings for CSV injection (checking if they start with `=`, `+`, `-`, `@`), a naive `value.lstrip().startswith(...)` allocates a new string via `lstrip()` for *every* value, even ones that don't start with whitespace. Since normal strings rarely start with whitespace, avoiding `lstrip()` is a huge win.

**Action:** Add a fast path to avoid `lstrip()` entirely for strings that don't start with a space:
```python
if value[0] in _DANGEROUS_PREFIXES:
    return f"'{value}"
if value[0].isspace() and value.lstrip().startswith(_DANGEROUS_PREFIXES):
    return f"'{value}"
```
This skips the `lstrip` allocation and `startswith` tuple checking for >99% of regular text, reducing overhead significantly.
