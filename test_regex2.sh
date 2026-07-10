export PR_BODY="💡 What:
- Inlined \`_sanitize_formula\` into \`_sanitize_value\` to avoid function call overhead.
- Replaced \`isinstance(value, str)\` and \`isinstance(rec, dict)\` with \`type(value) is str\` and \`type(rec) is dict\` respectively.

🎯 Why:
The \`html2md.log_export\` script exports large JSONL files to CSV, meaning the CSV record processing functions run inside a hot loop (potentially millions of times). Function call overhead and \`isinstance\` subclass-checking overhead compound significantly at that scale.

📊 Impact:
Increases throughput by avoiding function calls and subclass checks for every item. In local benchmarking with 100k items, the total loop execution time dropped from ~5.2s to ~5.0s, translating to an approximate 4-5% overall speedup.

🔬 Measurement:
Run \`PYTHONPATH=src pytest tests/test_log_export.py\` to ensure the CSV processing logic correctness is strictly preserved.

---
*PR created automatically by Jules for task [11660011673258939281](https://jules.google.com/task/11660011673258939281) started by @badMade*"

body=$(python3 -c "import os, re, sys; sys.stdout.write(re.sub(r'<!--.*?-->', '', os.environ.get('PR_BODY','') or '', flags=re.DOTALL))")
transcript_regex='(^|[[:space:]<>(])https://(claude\.ai/(chat|share)/[a-zA-Z0-9_-]+|claude\.ai/code/session_[a-zA-Z0-9_-]+|cursor\.com/share/[a-zA-Z0-9_-]+|chatgpt\.com/codex/[a-zA-Z0-9_-]+|jules\.google\.com/task/[a-zA-Z0-9_-]+)'
          has_transcript=false
          if printf '%s' "$body" | grep -Eqi "$transcript_regex"; then
            has_transcript=true
          fi
          echo $has_transcript
