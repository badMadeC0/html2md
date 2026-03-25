## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Python Fast Path String Processing Optimization

**Learning:** When sanitizing a massive dataset (like parsing JSONL to CSV) where strings are frequently checked for dangerous prefixes (e.g. for CSV injection using `.lstrip().startswith(...)`), relying solely on tuple matching and `.lstrip` has a very high overhead due to string allocations. Introducing a fast path `if value[0].isalnum(): return value` completely bypasses the `.lstrip` allocation and tuple matching for the vast majority of "normal" alphanumeric strings. This single C-implemented method check `isalnum()` provided an additional ~3x speedup on string sanitation (~0.40s down to ~0.12s per 1M iterations).
**Action:** When filtering or transforming strings in Python hot loops, first add a C-implemented fast path check (like `isalnum()`, `isalpha()`, or `isdigit()`) to quickly skip the expensive processing for normal, valid text inputs.
