## 2024-03-24 - [Avoid lstrip allocations in string processing]
**Learning:** In Python, string operations like `lstrip()` create new string objects, which involves memory allocation. This can be a bottleneck in tight loops or data processing functions.
**Action:** When conditionally parsing strings, check first characters or characters at index with quick string operations (like `str.isspace()`) before invoking expensive string allocation operations (like `lstrip()`).
