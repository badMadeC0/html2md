## 2024-06-18 - Missing Dependencies in CLI module
**Learning:** The `html2md.cli` module uses dynamic imports for `requests` and `markdownify`, and fails gracefully if they are missing. In this environment, they are missing.
**Action:** Focus performance optimization efforts on the `html2md.log_export` module since it doesn't have missing dependencies and is fully testable in this environment.

## 2024-06-18 - Performance bottlenecks in log_export.py
**Learning:** The `log_export.py` module spends significant time in `json.loads` and string manipulation. Specifically, `_sanitize_value` and `_sanitize_formula` function calls per row cell were found to be incredibly expensive. Inlining the sanitization logic reduced execution time by roughly 40%.
**Action:** Use inline sanitization inside the hot loop of `csv.writer` when handling millions of rows, rather than mapping individual field values through small helper functions.
