# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2023-10-25 - Python Micro-Optimizations vs Robustness
**Learning:** Two performance optimization attempts failed because they prioritized micro-speed over correctness and practical data shapes:
1. Using `type(value) is str` instead of `isinstance(value, str)` is slightly faster but inherently unsafe because it breaks compatibility with string subclasses (like Jinja2 `Markup` or translation strings), potentially bypassing security checks like CSV injection sanitization.
2. Adding `@lru_cache` to a function that processes log export values is a poor choice because log data (like timestamps, unique IDs, or full error messages) is highly variable. The overhead of hashing and dictionary lookups, combined with constant cache eviction (thrashing), makes it slower than simple fast-path character checks.

**Action:** Never use `type() is X` when inheritance/subclassing is a valid use case; stick to `isinstance`. Avoid memoization (`@lru_cache`) on functions that process high-cardinality/variable data streams, as the cache management overhead will outweigh any benefits.
