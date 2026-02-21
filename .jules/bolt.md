## 2024-05-22 - [Parallel Directory Creation Race Condition]
**Learning:** Checking for directory existence before creation (`if not os.path.exists(d): os.makedirs(d)`) is not thread-safe and leads to `FileExistsError` in parallel execution.
**Action:** Always use `os.makedirs(d, exist_ok=True)` in concurrent contexts to handle race conditions gracefully.
