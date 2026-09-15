## 2024-03-24 - [String Allocation on Hot Paths]
**Learning:** Checking for string conditions (like `.isspace()`) on a single character before calling allocation-heavy methods (like `.lstrip()`) can significantly speed up hot paths in data processing logic (like CSV sanitization).
**Action:** Always consider avoiding `.lstrip()`, `.rstrip()`, or `.replace()` when iterating through many records if you can quickly short-circuit the condition on the first/last character.
