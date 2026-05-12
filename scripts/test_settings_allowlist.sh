#!/usr/bin/env bash
# scripts/test_settings_allowlist.sh
# Verifies .claude/settings.json does NOT preapprove `git branch` forms
# whose ":*" suffix wildcard can be combined with destructive flags
# (-D / -d / -M / -m / --delete / --move). Per pr-rules/common.md, agents
# must not delete or rename branches, so every Bash(git branch ...)
# preapproval must be an explicit, complete, read-only form — no ":*"
# trailing wildcard on any `git branch` prefix.
#
# Usage: scripts/test_settings_allowlist.sh

set -u
fail() { echo "FAIL: $*" >&2; exit 1; }

if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi
cd "$ROOT" || fail "cannot cd to repo root: $ROOT"

SETTINGS=".claude/settings.json"
[ -f "$SETTINGS" ] || fail "$SETTINGS missing"

# Probe for any python >= 3.8 (json is stdlib so no extra deps needed).
# Match the interpreter-discovery idiom from scripts/test_baseline_hook.sh:
# absolute system paths first to avoid a broken pyenv shim blocking the test.
PYTHON_BIN=""
for candidate in /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 python; do
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done
[ -n "$PYTHON_BIN" ] || fail "no python >= 3.8 interpreter found"

BAD=$("$PYTHON_BIN" - "$SETTINGS" <<'PY'
import json, sys, re
with open(sys.argv[1]) as f:
    data = json.load(f)
allow = data.get("permissions", {}).get("allow", [])
# Match `Bash(git branch ... :*)`. The `:*` suffix in Claude permission
# rules means "any arguments allowed here" — combined with a `git branch`
# prefix, that can include destructive flags like -D/-d/-M/-m/--delete/
# --move. Verified empirically: `git branch -v -D <name>` deletes a
# branch and would match the rule `Bash(git branch -v:*)`.
wildcard_re = re.compile(r'^Bash\(git branch\b.*:\*\)$')
bad = [e for e in allow if e.startswith("Bash(git branch") and wildcard_re.match(e)]
for b in bad:
    print(b)
sys.exit(0 if not bad else 1)
PY
)
if [ $? -ne 0 ]; then
  echo 'FAIL: the following Bash(git branch ...) allowlist entries use a ":*" wildcard that can be combined with destructive flags (-D/-d/-M/-m/--delete/--move):' >&2
  echo "$BAD" >&2
  echo 'Replace each entry with explicit read-only invocations (no ":*" suffix). See pr-rules/common.md.' >&2
  exit 1
fi

echo "ok: no destructive-wildcard git-branch allowlist entries in $SETTINGS"
