## 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:
1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-06-11 - Python Sub-String and Tuple `startswith` Optimizations

**Learning:** While `startswith` with a tuple is generally fast, in highly hot loops, an O(1) character lookup (`value[0] in "=+-@"`) is approximately 2x faster than `.startswith(("=", "+", "-", "@"))` which has to evaluate each prefix sequentially in C. Furthermore, conditionally calling `.lstrip()` only when `value[0].isspace()` prevents redundant string scans and allocations for non-whitespace strings, yielding ~25% overall faster JSONL-to-CSV exporting.
**Action:** Replace `startswith(tuple_of_single_chars)` with `string[0] in string_of_chars` when checking prefixes of length 1, and only apply `.lstrip()` when `string[0].isspace()` is true in hot string sanitization loops.
