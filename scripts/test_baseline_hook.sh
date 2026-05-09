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

# Probe candidates and pick the first one that satisfies >= 3.8.
# Absolute system paths come first so the test avoids broken pyenv shims
# when the repo's `.python-version` pins an uninstalled version. Bare
# `python3`/`python` remain as fallbacks for normal developer shells.
PYTHON_BIN=""
for candidate in /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 python3 python; do
  if [ -x "$candidate" ] || command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" >/dev/null 2>&1; then
      PYTHON_BIN="$candidate"
      break
    fi
  fi
done
[ -n "$PYTHON_BIN" ] || fail "no python interpreter >= 3.8 found (tried: /usr/bin/python3, /opt/homebrew/bin/python3, /usr/local/bin/python3, python3, python)"

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

# Verify the actual Claude settings command can launch the hook even when a
# bare `python` on PATH is broken/unusable. This covers pyenv checkouts where
# `.python-version` points at an uninstalled version and a usable `python3` or
# system interpreter is still available.
SETTINGS_HOOK_COMMAND="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path

settings = json.loads(Path(".claude/settings.json").read_text(encoding="utf-8"))
print(settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"])
PY
)"
case "$SETTINGS_HOOK_COMMAND" in
  "python $HOOK") fail "settings hook command must not rely on bare python only" ;;
esac

TMP_HOOK_PATH="$(mktemp -d)"
cleanup_tmp_hook_path() { rm -rf "$TMP_HOOK_PATH"; }
trap cleanup_tmp_hook_path EXIT
cat >"$TMP_HOOK_PATH/python" <<'SH'
#!/usr/bin/env sh
echo "simulated broken python" >&2
exit 127
SH
chmod +x "$TMP_HOOK_PATH/python"
PYTHON_EXE="$("$PYTHON_BIN" -c 'import sys; print(sys.executable)')"
cat >"$TMP_HOOK_PATH/python3" <<SH
#!/usr/bin/env sh
exec "$PYTHON_EXE" "\$@"
SH
chmod +x "$TMP_HOOK_PATH/python3"

if ! printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":"README.md"}}' \
    | PATH="$TMP_HOOK_PATH:$PATH" /bin/sh -c "$SETTINGS_HOOK_COMMAND" >/dev/null 2>&1; then
  fail "settings hook command should ALLOW normal file when bare python is broken"
fi
pass "settings hook command runs with broken bare python"

if printf '%s\n' '{"hook_event_name":"PreToolUse","tool_name":"Write","tool_input":{"file_path":".env"}}' \
    | PATH="$TMP_HOOK_PATH:$PATH" /bin/sh -c "$SETTINGS_HOOK_COMMAND" >/dev/null 2>&1; then
  fail "settings hook command should preserve hook BLOCK result for sensitive files"
fi
pass "settings hook command preserves sensitive-file block"

# --- BLOCK cases (expect non-zero exit) ---
for path in ".env" ".env.local" ".env.production" "config/.env" \
            ".envrc" ".envrc.local" "config/.envrc" \
            "secrets.pem" "server.key" "credentials.json" \
            "deploy.crt" "id_rsa" "id_rsa.pub" "id_rsa_old" \
            "src/keys/id_rsa" \
            "secrets.json" "secret.json" "secrets.yaml" "secret.yml" \
            "secrets.toml" "secret.toml" "secrets.env" \
            "config/secrets.json" "config/secrets.toml" \
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
