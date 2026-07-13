## 2024-07-13 - Optimize CSV formula sanitization
**Learning:** Checking for string whitespace using `.isspace()` on the first character before applying `.lstrip()` can avoid string allocation overhead in the fast-path for non-formula strings.
**Action:** When handling string manipulation operations that trigger new string allocations like `.lstrip()`, check preconditions first to bypass the allocation step on common valid inputs.
