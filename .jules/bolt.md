## 2024-10-24 - Fast Path String Evaluation in CSV Export
**Learning:** `json.loads` generates strings rapidly. Calling `.lstrip().startswith()` on every string value in the CSV export loop created a significant bottleneck due to constant string allocation.
**Action:** Add a fast-path check `first_char = value[0]` to evaluate if the string even begins with whitespace or a dangerous character before invoking expensive string methods like `.lstrip()`. Furthermore, using `type(value) is str` is measurably faster than `isinstance(value, str)` on hot paths where subclasses are not expected.
