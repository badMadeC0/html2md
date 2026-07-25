## 2024-05-19 - Fast path string checking in log_export
**Learning:** Checking `value[0].isspace()` before calling `value.lstrip()` prevents unnecessary string allocations for standard strings that don't start with space. Since `_sanitize_formula` runs per cell during export, avoiding string allocations on every normal cell provides measurable performance improvements without complicating the logic.
**Action:** Before executing string transformations like `.lstrip()`, check if the transformation is even necessary by evaluating a fast condition like `isspace()` if applicable.
