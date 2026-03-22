## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Python Function Call & Attribute Lookup Overhead in Hot Loops
**Learning:** In very tight hot loops (like reading JSON and writing CSV records), the overhead of function calls and attribute lookups becomes measurable.
1. Inlining small functions (like `_sanitize_formula` into `_sanitize_value`) avoids function call overhead.
2. Hoisting method lookups (like `get = rec.get` before a list comprehension) avoids repeated attribute lookups for each item in the list comprehension. This yielded a solid performance improvement in benchmarking.
3. String prefixes and suffix checking can be significantly faster by just testing single characters against a tuple of chars or `in "=+-@"` string (if length 1). Also using `.lstrip().startswith(tuple)` is fast and safe.

**Action:** When optimizing loop-heavy Python code, look for opportunities to inline tiny helper functions and hoist attribute/method lookups out of inner loops and comprehensions.
