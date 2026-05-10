#!/usr/bin/env bash
# scripts/test_baseline_hook.sh
# Smoke test for .claude/hooks/protect-sensitive-files.py.
#
# The hook reads a Claude Code PreToolUse JSON payload on stdin and must:
#   - Exit non-zero (block) when the tool would Edit/Write a sensitive path
#     (.env, .env.*, *.pem, *.key, credentials.json, *.crt, id_rsa*).
#   - Exit zero (allow) for normal source paths.
#
# Usage: scripts/test_baseline_hook.sh

set -u
fail() { echo "FAIL: $*" >&2; exit 1; }
pass() { echo "ok:   $*"; }

if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi
cd "$ROOT" || fail "cannot cd to repo root: $ROOT"

HOOK=".claude/hooks/protect-sensitive-files.py"
[ -f "$HOOK" ] || fail "hook script not found: $HOOK"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
else
  fail "python interpreter not found (expected 'python' or 'python3')"
fi

"$PYTHON_BIN" - <<'PY' >/dev/null 2>&1 || fail "python interpreter must be >= 3.8"
import sys
sys.exit(0 if sys.version_info >= (3, 8) else 1)
PY
PYTHON_BIN_PATH="$($PYTHON_BIN - <<'PY'
import sys
print(sys.executable)
PY
)" || fail "could not resolve python interpreter: $PYTHON_BIN"

SETTINGS_HOOK_COMMAND="$($PYTHON_BIN - <<'PY'
import json
from pathlib import Path

settings = json.loads(Path(".claude/settings.json").read_text(encoding="utf-8"))
print(settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"])
PY
)" || fail "could not read hook command from .claude/settings.json"

# Helper: run the hook with a given tool_name and file_path; return its exit code.
run_hook() {
  local tool="$1" path="$2"
  "$PYTHON_BIN" "$HOOK" <<EOF
{
  "hook_event_name": "PreToolUse",
  "tool_name": "$tool",
  "tool_input": { "file_path": "$path" }
}
EOF
}

run_hook_payload() {
  local payload="$1"
  printf "%s\n" "$payload" | "$PYTHON_BIN" "$HOOK"
}

# Ensure the configured Claude hook command skips an unusable `python` shim
# (for example, pyenv with a missing .python-version) when `python3` works.
TMP_DIR="$(mktemp -d)" || fail "could not create temporary directory"
cleanup_tmp_dir() { rm -rf "$TMP_DIR"; }
trap cleanup_tmp_dir EXIT
cat >"$TMP_DIR/python" <<'SH'
#!/usr/bin/env sh
echo "simulated broken python" >&2
exit 127
SH
cat >"$TMP_DIR/python3" <<SH
#!/usr/bin/env sh
exec "$PYTHON_BIN_PATH" "\$@"
SH
chmod +x "$TMP_DIR/python" "$TMP_DIR/python3"
if ! PATH="$TMP_DIR:$PATH" sh -c "$SETTINGS_HOOK_COMMAND" <<'EOF' >/dev/null 2>&1; then
{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"src/html2md/cli.py"}}
EOF
  fail "settings hook command should use working python3 when python is unavailable"
fi
pass "settings hook command uses working python3 when python is unavailable"

NO_PYTHON_DIR="$TMP_DIR/no-usable-python"
mkdir "$NO_PYTHON_DIR" || fail "could not create no-usable-python directory"
cat >"$NO_PYTHON_DIR/python" <<'SH'
#!/bin/sh
echo "simulated missing python" >&2
exit 127
SH
cat >"$NO_PYTHON_DIR/python3" <<'SH'
#!/bin/sh
echo "simulated missing python3" >&2
exit 127
SH
chmod +x "$NO_PYTHON_DIR/python" "$NO_PYTHON_DIR/python3"
PATH="$NO_PYTHON_DIR" /bin/sh -c "$SETTINGS_HOOK_COMMAND" <<'EOF' >/dev/null 2>&1
{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"src/html2md/cli.py"}}
EOF
NO_PYTHON_STATUS=$?
if [ "$NO_PYTHON_STATUS" -ne 2 ]; then
  fail "settings hook command should exit 2 when no usable Python is available, got $NO_PYTHON_STATUS"
fi
pass "settings hook command exits 2 when no usable Python is available"

# --- BLOCK cases (expect non-zero exit) ---
for path in ".env" ".env.local" ".env.production" "config/.env" \
            ".envrc" ".envrc.local" "config/.envrc" \
            "secrets.pem" "server.key" "credentials.json" \
            "deploy.crt" "id_rsa" "id_rsa.pub" "id_rsa_old" \
            "src/keys/id_rsa" \
            "secrets.json" "secret.json" "secrets.yaml" "secret.yml" \
            "config/secrets.json" \
            "prod.secret.yaml" "app.secrets.yml" \
            "api-token.txt" "my_api_token.json" \
            "team-credentials.toml" "service_credentials.txt"; do
  if run_hook "Write" "$path" >/dev/null 2>&1; then
    fail "hook should BLOCK Write to '$path' but allowed it"
  fi
  pass "blocked Write to '$path'"
  if run_hook "Edit" "$path" >/dev/null 2>&1; then
    fail "hook should BLOCK Edit to '$path' but allowed it"
  fi
  pass "blocked Edit to '$path'"
done

if run_hook_payload '{"hook_event_name":"PreToolUse","tool_name":"MultiEdit","tool_input":{"edits":[{"path":"src\\keys\\id_rsa"}]}}' >/dev/null 2>&1; then
  fail "hook should BLOCK MultiEdit nested path 'src\\keys\\id_rsa' but allowed it"
fi
pass "blocked MultiEdit nested path 'src\\keys\\id_rsa'"

if run_hook_payload '{"hook_event_name":"PreToolUse","tool_name":"NotebookEdit","tool_input":{"edits":[{"notebook_path":"config/.env"}]}}' >/dev/null 2>&1; then
  fail "hook should BLOCK NotebookEdit nested notebook_path 'config/.env' but allowed it"
fi
pass "blocked NotebookEdit nested notebook_path 'config/.env'"

# --- FAIL-CLOSED cases: malformed input must block, not allow ---
if printf '' | "$PYTHON_BIN" "$HOOK" >/dev/null 2>&1; then
  fail "hook should BLOCK on empty stdin (fail-closed) but allowed it"
fi
pass "blocked empty stdin (fail-closed)"

if printf 'not-json{' | "$PYTHON_BIN" "$HOOK" >/dev/null 2>&1; then
  fail "hook should BLOCK on malformed JSON (fail-closed) but allowed it"
fi
pass "blocked malformed JSON (fail-closed)"

# In-scope tool with no recognized path keys must fail closed (unknown
# payload shape — could be a new tool variant the hook doesn't know).
if run_hook_payload '{"hook_event_name":"PreToolUse","tool_name":"Edit","tool_input":{"target":"src/foo.py"}}' >/dev/null 2>&1; then
  fail "hook should BLOCK in-scope tool with no recognized path keys (fail-closed) but allowed it"
fi
pass "blocked in-scope tool with unknown payload shape (fail-closed)"

if run_hook_payload '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{}}' >/dev/null 2>&1; then
  fail "hook should BLOCK in-scope tool with empty tool_input (fail-closed) but allowed it"
fi
pass "blocked in-scope tool with empty tool_input (fail-closed)"

# --- ALLOW cases (expect zero exit) ---
for path in "src/html2md/cli.py" "README.md" "tests/test_cli_smoke.py" \
            "docs/overview.md" "pyproject.toml" "envoy.yaml" \
            "src/secrets_loader.py"; do
  if ! run_hook "Write" "$path" >/dev/null 2>&1; then
    fail "hook should ALLOW Write to '$path' but blocked it"
  fi
  pass "allowed Write to '$path'"
done

echo "OK: protect-sensitive-files.py blocks sensitive paths and allows normal paths"
