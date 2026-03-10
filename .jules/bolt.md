## 2025-03-10 - JSON parsing optimization in log export
**Learning:** Checking for space string or empty string `if not line or line.isspace()` before calling `json.loads` is significantly faster than calling `.strip()` on every line, since `json.loads` handles leading/trailing whitespace perfectly without the extra overhead of `strip()` creating new strings.
**Action:** When iterating over JSONL or text files and passing lines to `json.loads`, prefer `if not line or line.isspace(): continue` instead of calling `line.strip()` first to save string allocation overhead.
