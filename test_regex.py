import re

body = """💡 **What**: Added an `isspace()` check to `_sanitize_formula` in `src/html2md/log_export.py` to prevent unnecessary calls to `lstrip()` for standard alphanumeric text.

🎯 **Why**: `str.lstrip()` allocates a new string in memory. Previously, it was called on *every* string not starting directly with a dangerous prefix to check if it was whitespace-padded. In a hot loop processing large logs, this caused significant overhead and memory allocation churn.

📊 **Impact**: Benchmarking showed a measurable speedup (around 1.6x faster on a mixed dataset) in string sanitization, leading to faster log exports and reduced memory allocations.

🔬 **Measurement**: Verify by benchmarking the `_sanitize_formula` function with standard non-whitespace text. The performance delta is clearly visible. Tests have been run and confirm no regressions in functionality.

---
*PR created automatically by Jules for task [10586565146730865587](https://jules.google.com/task/10586565146730865587) started by @badMade*
"""

# Regex from the bash script (using Python logic here to inspect)
transcript_regex = r'(^|[ \t\n\r\f\v<>(])https://(claude\.ai/(chat|share)/[a-zA-Z0-9_-]+|claude\.ai/code/session_[a-zA-Z0-9_-]+|cursor\.com/share/[a-zA-Z0-9_-]+|chatgpt\.com/codex/[a-zA-Z0-9_-]+|jules\.google\.com/task/[a-zA-Z0-9_-]+)'

m = re.search(transcript_regex, body, re.IGNORECASE)
if m:
    print("Match found:")
    print(m.group(0))
else:
    print("No match")
