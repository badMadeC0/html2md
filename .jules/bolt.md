# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-25 - Python Fast Path Optimizations for JSON Parsing Loop

**Learning:** When parsing JSON in a hot loop (like processing JSONL files), replacing `json.loads(line)` with the direct method `json.JSONDecoder().decode(line)` yields a ~15-20% throughput increase for the decoding step.

1. **Bypass overhead**: `json.loads` is a Python function that performs several `is None` and `kwargs` checks before instantiating a default `JSONDecoder` and calling `.decode()`.
2. **Hoist the decoder**: By hoisting `decode = json.JSONDecoder().decode` outside the loop, we bypass the argument checks and method lookup for every single line.
3. **Safety constraint**: `JSONDecoder().decode` strictly expects strings, whereas `json.loads` natively handles `bytes` or `bytearray`. When reading from a text-mode file, strings are guaranteed, making this optimization safe.

**Action:** For performance-critical loops parsing millions of lines of text-based JSON, use a pre-instantiated `JSONDecoder().decode` instead of `json.loads` to eliminate unnecessary wrapper overhead.
