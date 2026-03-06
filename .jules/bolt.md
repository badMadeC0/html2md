# Bolt's Journal

## 2024-05-14 - Optimizing CSV export by inlining string checks and using list comprehensions
**Learning:** `csv.DictWriter` is significantly slower than `csv.writer` when handling hundreds of thousands of rows. Also, repeatedly calling `.startswith()` with a tuple and `.lstrip()` on every value in a large dataset adds significant overhead. Checking the first character (`value[0]`) before calling string methods is much faster for the common path (where the string doesn't start with a dangerous character).
**Action:** Replace `csv.DictWriter` with `csv.writer` and list comprehensions. Optimize the `_sanitize_formula` function to check the first character and short-circuit early. Combine `_sanitize_value` and `_sanitize_formula` to avoid double function calls.
