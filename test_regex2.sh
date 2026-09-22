export PR_BODY='[4224400451671403390](https://jules.google.com/task/4224400451671403390)'
body=$(python3 -c "import os, re, sys; sys.stdout.write(re.sub(r'<!--.*?-->', '', os.environ.get('PR_BODY','') or '', flags=re.DOTALL))")
transcript_regex='(^|[[:space:]<>(])https://(claude\.ai/(chat|share)/[a-zA-Z0-9_-]+|claude\.ai/code/session_[a-zA-Z0-9_-]+|cursor\.com/share/[a-zA-Z0-9_-]+|chatgpt\.com/codex/[a-zA-Z0-9_-]+|jules\.google\.com/task/[a-zA-Z0-9_-]+)'

printf '%s' "$body" | grep -Eqi "$transcript_regex" && echo "MATCH" || echo "NO MATCH"
printf '%s' "$body" | grep -Eoi "$transcript_regex"
