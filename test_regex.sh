PR_BODY='💡 What: Inlined the string sanitization logic into `_sanitize_value`, used exact type checking (`type(x) is dict` instead of `isinstance()`), replaced string membership tuple checks with string exact match `value[0] in "=+-@"`, and converted generator expressions into list comprehensions.
🎯 Why: Function call overhead and `isinstance()` MRO traversal were slowing down a very tight hot loop processing JSON logs to CSV (field by field, record by record).
📊 Impact: Reduced the per-record overhead significantly. Benchmarks on an equivalent tight loop show ~20-30% faster sanitization throughput.
🔬 Measurement: Run the test suite or verify with large JSONL file conversions.

---
*PR created automatically by Jules for task [4224400451671403390](https://jules.google.com/task/4224400451671403390) started by @badMade*'

body=$(python3 -c "import os, re, sys; sys.stdout.write(re.sub(r'<!--.*?-->', '', os.environ.get('PR_BODY','') or '', flags=re.DOTALL))")
transcript_regex='(^|[[:space:]<>(])https://(claude\.ai/(chat|share)/[a-zA-Z0-9_-]+|claude\.ai/code/session_[a-zA-Z0-9_-]+|cursor\.com/share/[a-zA-Z0-9_-]+|chatgpt\.com/codex/[a-zA-Z0-9_-]+|jules\.google\.com/task/[a-zA-Z0-9_-]+)'

if printf '%s' "$body" | grep -Eqi "$transcript_regex"; then
  echo "MATCH"
else
  echo "NO MATCH"
fi
