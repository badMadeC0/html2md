# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~10% throughput increase through several specific optimizations:

1. **Avoid Subclass Checks (`isinstance`)**: Using `type(x) is dict` and `type(x) is str` instead of `isinstance()` avoids the overhead of checking subclasses. Since `json.loads` creates pure `dict` and `str` types, this is perfectly safe and faster.
2. **Inline Fast Paths**: Instead of calling a function (`_sanitize_formula`) from within another function (`_sanitize_value`), we combined them so the fast path (where the value is just returned) avoids multiple function call overheads.
3. **Cache Lookups**: Caching `dict.get` as a local `get` function reduces attribute lookup overhead during the list comprehension in the loop.

**Action:** Apply `type(x) is` for exact type checking in hot loops when exact types are guaranteed (like from JSON parsing), and always seek to inline simple conditional fast-paths to avoid function call overhead.
