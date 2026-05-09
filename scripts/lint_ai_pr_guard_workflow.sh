#!/usr/bin/env bash
# scripts/lint_ai_pr_guard_workflow.sh
# Lints .github/workflows/ai-assisted-pr-guard.yml.
#
# Asserts:
#   - file exists
#   - has on.pull_request triggers
#   - defines at least one job
#   - references the [AI-Assisted] PR-title marker
#   - references a Claude chat URL check (claude.ai or CLAUDE_CHAT_URL placeholder)
#
# Uses pyyaml when available (it is a declared runtime dep of html2md-cli);
# otherwise falls back to grep-based structural checks so the test stays
# runnable in fresh environments where deps aren't yet installed.

set -u
fail() { echo "FAIL: $*" >&2; exit 1; }

if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi
cd "$ROOT" || fail "cannot cd to repo root: $ROOT"

WF=".github/workflows/ai-assisted-pr-guard.yml"
[ -f "$WF" ] || fail "workflow not found: $WF"

# Prefer pyyaml-based parse; fall back to grep checks.
# Probe candidates and pick the first one that satisfies >= 3.8.
# `python3`/`python` come first so the lint runs in a developer's normal
# shell environment. The absolute system paths come next so the lint still
# runs when the repo's `.python-version` pins a pyenv version that isn't
# installed (the pyenv shim would otherwise fail before reaching a usable
# interpreter, and the grep-only path silently downgrades validation).
have_yaml=0
PYTHON_BIN=""
for candidate in python3 python /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done

if [ -n "$PYTHON_BIN" ] && "$PYTHON_BIN" -c "import yaml" >/dev/null 2>&1; then
  have_yaml=1
fi

if [ "$have_yaml" -eq 1 ]; then
  "$PYTHON_BIN" - "$WF" <<'PY' || exit 1
import sys
import yaml

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    raw = f.read()
try:
    doc = yaml.safe_load(raw)
except yaml.YAMLError as e:
    print(f"FAIL: {path} is not valid YAML: {e}", file=sys.stderr)
    sys.exit(1)

if not isinstance(doc, dict):
    print(f"FAIL: {path} top-level must be a mapping", file=sys.stderr)
    sys.exit(1)

# YAML parses bare 'on:' as boolean True; accept either key.
on_block = doc.get("on", doc.get(True))
if on_block is None:
    print("FAIL: workflow missing 'on:' block", file=sys.stderr); sys.exit(1)
if isinstance(on_block, dict):
    if "pull_request" not in on_block:
        print("FAIL: workflow must trigger on pull_request", file=sys.stderr); sys.exit(1)
elif isinstance(on_block, list):
    if "pull_request" not in on_block:
        print("FAIL: workflow must trigger on pull_request", file=sys.stderr); sys.exit(1)
else:
    print(f"FAIL: unexpected 'on' shape: {type(on_block).__name__}", file=sys.stderr); sys.exit(1)

jobs = doc.get("jobs")
if not isinstance(jobs, dict) or not jobs:
    print("FAIL: workflow must define at least one job", file=sys.stderr); sys.exit(1)

if "[AI-Assisted]" not in raw:
    print("FAIL: workflow must reference the [AI-Assisted] PR-title marker", file=sys.stderr); sys.exit(1)
if "claude.ai" not in raw and "CLAUDE_CHAT_URL" not in raw and "Claude chat" not in raw:
    print("FAIL: workflow must reference a Claude chat link check", file=sys.stderr); sys.exit(1)

print(f"OK [yaml-parse]: {path} triggers on pull_request, has {len(jobs)} job(s), checks [AI-Assisted] + Claude chat link")
PY
else
  # Fallback grep-based checks (no pyyaml available).
  grep -Eq '^[[:space:]]*pull_request:' "$WF" || fail "workflow must trigger on pull_request (grep)"
  grep -Eq '^[[:space:]]*jobs:' "$WF" || fail "workflow must define a 'jobs:' block (grep)"
  grep -Fq '[AI-Assisted]' "$WF" || fail "workflow must reference the [AI-Assisted] PR-title marker (grep)"
  if ! grep -Eq 'claude\.ai|CLAUDE_CHAT_URL|Claude chat' "$WF"; then
    fail "workflow must reference a Claude chat link check (grep)"
  fi
  echo "OK [grep-only, pyyaml not installed]: $WF triggers on pull_request, has jobs, checks [AI-Assisted] + Claude chat link"
fi
