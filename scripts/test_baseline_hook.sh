#!/usr/bin/env bash
# scripts/test_baseline_hook.sh
# Smoke test for .claude/hooks/protect-sensitive-files.py.
#
# The hook reads a Claude Code PreToolUse JSON payload on stdin and must:
#   - Exit non-zero (block) when the tool would Edit/Write a sensitive path.
#     The canonical pattern set is documented in pr-rules/common.md §3 and
#     enforced by .claude/hooks/protect-sensitive-files.py's
#     SENSITIVE_BASENAME_PATTERNS — covers .env*, *.pem, *.key, *.crt,
#     id_{rsa,ed25519,ecdsa,dsa}*, credentials.*, secret.*/secrets.*,
#     *.secret(s).*, *api[-_]token*, *[-_]credentials.* and more.
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
# Try absolute system paths FIRST. The `python3`/`python` shell names
# can resolve to a pyenv shim pinned to an uninstalled version, which
# may hang or fail before the probe times out. Putting known-good
# absolute paths first means a broken shim never blocks the test.
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

# --- BLOCK cases (expect non-zero exit) ---
for path in ".env" ".env.local" ".env.production" "config/.env" \
            ".envrc" ".envrc.local" "config/.envrc" \
            "secrets.pem" "server.key" "credentials.json" \
            "deploy.crt" "id_rsa" "id_rsa.pub" "id_rsa_old" \
            "src/keys/id_rsa" \
            "id_ed25519" "id_ed25519.pub" \
            "id_ecdsa" "id_ecdsa.pub" \
            "id_dsa" \
            ".ssh/id_ed25519" "src/keys/id_ecdsa" \
            "secrets.json" "secret.json" "secrets.yaml" "secret.yml" \
            "secrets.toml" "secret.toml" "secrets.env" \
            "config/secrets.json" "config/secrets.toml" \
            "prod.secret.yaml" "app.secrets.yml" \
            "api-token.txt" "my_api_token.json" \
            "team-credentials.toml" "service_credentials.txt" \
            "credentials.yaml" "credentials.yml" "credentials.toml" \
            "secrets" "secret" "credentials" \
            "config/secrets" "vault/credentials" \
            "prod-credentials" "prod_credentials" \
            "secrets/prod.json" "secrets/anything.yaml" \
            "credentials/token.json" "config/credentials/cert.pem" \
            "secret/foo.txt" "deep/path/to/secrets/file.dat"; do
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
