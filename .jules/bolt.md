# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.
## 2026-04-24 - [Avoid String Allocations in Hot Paths]
**Learning:** `value.lstrip()` creates a new string on every call, even if there are no leading spaces. In the CSV sanitization loop (`_sanitize_formula`), this was executing on hundreds of thousands of valid string fields.
**Action:** Avoid expensive string manipulation methods like `lstrip()` in hot paths unless absolutely necessary. A fast check (`first = value[0]`) can conditionally bypass the expensive call (`first.isspace() and value.lstrip().startswith(...)`), significantly improving performance without changing semantics.

## 2026-04-24 - [Type Check vs Isinstance for JSON parsing]
**Learning:** `json.loads` will strictly produce native strings. `type(value) is str` is measurably faster than `isinstance(value, str)` since it avoids Method Resolution Order (MRO) traversal overhead.
**Action:** When you know a value originates from a strict parser (like `json.loads`) and you don't expect subclasses, prefer exact type checking (`type(...) is str`) in hot loops for a slight speedup.
