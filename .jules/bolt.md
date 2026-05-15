# 2024-05-24 - Python Fast Path Optimizations for CSV/JSON Export Loop

**Learning:** Optimizing a hot loop parsing JSON to CSV in Python yielded ~40% throughput increase through several specific optimizations:

1. **Short-circuit string checks**: Before doing expensive string manipulation like `value.lstrip().startswith(...)`, checking the first character `first_char = value[0]` and conditionally running the `lstrip` only when `first_char.isspace()` avoids generating a new string for `lstrip()` and the overhead of `.startswith` for the vast majority of non-formula values.
2. **Avoid Exceptions in Loops**: Adding `if line.isspace(): continue` prevents throwing and catching a `json.JSONDecodeError` on empty or whitespace-only lines. In Python, exception handling is relatively slow, so avoiding unnecessary exceptions in a file-processing loop is a solid performance win.

**Action:** When optimizing data-processing hot loops in Python, first eliminate string allocations (`strip`, `lstrip`), and avoid catching exceptions on predictable data shapes (like blank lines). Always keep `isinstance` instead of strict `type() is X` checks unless strictly necessary to avoid breaking polymorphism.
