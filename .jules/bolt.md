## 2023-10-27 - [Optimize CSV export sanitization]
**Learning:** Found an unnecessary expensive string operation in a hot path in `log_export.py`. Calling `.lstrip()` on long strings inside a loop processing JSONL to CSV was a noticeable bottleneck.
**Action:** When sanitizing strings against prefixes, add a fast-path check like `value[0].isspace()` to short-circuit expensive operations like `.lstrip()` for standard inputs.
