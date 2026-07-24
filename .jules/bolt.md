# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Rely on native parsers**: Instead of calling `.strip()` and checking truthiness on every line, let `json.loads()` handle whitespace (it ignores it natively) and gracefully catch the `JSONDecodeError` for empty or bad lines. This avoids redundant string allocations and checks.
2. **Loop variable hoisting**: Pre-extracting mapping values (`[name for name, _ in mapping]`) into a simple list before the main loop avoids unpacking tuples (`for name, _ in mapping`) during the list comprehension run for every single record, which was adding measurable overhead.
3. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, check the first character or empty string fast path `not value or value[0] == "'"`. This avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
4. **Fast type checks**: Using `type(rec) is dict` instead of `isinstance(rec, dict)` and `type(value) is str` instead of `isinstance(value, str)` skips subclass checks and is slightly faster in very tight loops.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), pre-compute list comprehenson iterables to avoid unpacking in the loop, and use `type() is X` for exact type checking instead of `isinstance` if subclassing isn't a concern.

## 2024-05-27 - Python String Method Overhead vs Short-Circuiting

**Learning:** Replacing an `isinstance()` check with a `type() is` check in Python is an anti-pattern. While it might yield nanoseconds of improvement, it breaks polymorphic type checking and violates the "no micro-optimizations without measurable impact" rule. The real measurable performance improvement comes from avoiding expensive string manipulation like `lstrip()` by adding a cheap condition (like `value[0].isspace()`) that short-circuits the evaluation. Additionally, `in frozenset` lookup is slightly faster than `in tuple` lookup, which also contributes nicely.

**Action:** Avoid replacing `isinstance` with `type` in the name of micro-optimizations. Focus on avoiding expensive built-in string methods (like `lstrip()` which returns a new string and copies data) by guarding them with cheaper character-level checks (like `isspace()`) when you know those methods will do no useful work on most inputs.
