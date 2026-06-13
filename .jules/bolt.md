# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Guarding String Allocations with Character Checks

**Learning:** When sanitizing strings (like for CSV injection prevention), a common pattern is to check for dangerous prefixes after stripping whitespace: `value.lstrip().startswith(...)`. While short-circuiting this with a check on the first character helps, we still end up allocating a new string with `lstrip()` for any string containing spaces. A much faster approach for the majority of strings (which don't start with spaces) is to guard the `lstrip()` call entirely by checking if the first character is a space: `c.isspace() and value.lstrip().startswith(...)`. This yielded an additional ~35% speedup for standard alphanumeric strings in our CSV export loop.

**Action:** Whenever using `strip()` or `lstrip()` conditionally based on the beginning of a string, consider guarding the expensive allocation with a cheap `isspace()` check on the first character.
