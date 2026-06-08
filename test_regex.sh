body="💡 What: Added an early fast-path check (\`first.isspace()\`) in \`_sanitize_formula\` to avoid calling \`.lstrip()\` on strings that don't start with whitespace. Also changed the character lookup for dangerous prefixes to use a string (\`_DANGEROUS_PREFIX_STR\`) instead of a tuple.
🎯 Why: \`_sanitize_formula\` is called for every field of every record in the JSONL log export. Most string values are regular strings (e.g. \`status=\"ok\"\`). Calling \`.lstrip()\` on every string allocates a new string unnecessarily.
📊 Impact: Expected performance improvement in JSON-to-CSV exporting for large logs. The \`_sanitize_formula\` function runs ~30-40% faster for mixed inputs because it avoids allocating new strings for regular text.
🔬 Measurement: Run a timeit benchmark on \`_sanitize_formula\` passing regular alphanumeric strings. Observe the speed difference. Tested to ensure no regressions with \`pytest tests/test_log_export.py tests/test_csv_security.py\`.

---
*PR created automatically by Jules for task [4076921269183034811](https://jules.google.com/task/4076921269183034811) started by @badMade*"

transcript_regex='(^|[[:space:]<>(])https://(claude\.ai/(chat|share)/[a-zA-Z0-9_-]+|claude\.ai/code/session_[a-zA-Z0-9_-]+|cursor\.com/share/[a-zA-Z0-9_-]+|chatgpt\.com/codex/[a-zA-Z0-9_-]+|jules\.google\.com/task/[a-zA-Z0-9_-]+)'

if printf '%s' "$body" | grep -Eqi "$transcript_regex"; then
  echo "MATCH"
else
  echo "NO MATCH"
fi
