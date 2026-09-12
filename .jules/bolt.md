# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2024-05-24 - Short-Circuiting Expensive String Operations in Sanitization Loops

**Learning:** Optimizing a string sanitization function (`_sanitize_formula`) inside a hot loop by adding a fast path check (`first_char.isspace()`) before executing expensive string manipulations (`lstrip()` and `startswith()`) resulted in a ~19% performance improvement for string processing.
The original code checked `if value[0] in _DANGEROUS_PREFIXES or value.lstrip().startswith(_DANGEROUS_PREFIXES):`. This meant that for normal strings not starting with dangerous prefixes, it still executed the `.lstrip()` and `.startswith()` methods.
By first extracting `first_char = value[0]` and then checking `first_char.isspace()`, we avoid these expensive method calls for the vast majority of regular text strings. `str.isspace()` correctly handles the same whitespace character definitions as `lstrip()`.

**Action:** When sanitizing strings against prefixes in performance-critical loops, avoid unconditionally running `.lstrip()` or `.strip()`. Instead, check if the first character is whitespace (via `.isspace()`) to short-circuit the logic for normal alphanumeric text strings.
