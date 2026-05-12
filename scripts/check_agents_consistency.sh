#!/usr/bin/env bash
# scripts/check_agents_consistency.sh
# Verifies the AI-PR-Review baseline structure is well-formed.
# Exits 0 on success; non-zero with a diagnostic on the first failure.
#
# Checks:
#   1. AGENTS.md exists and is a regular file.
#   2. AGENTS.md contains <!-- BEGIN BASELINE --> and <!-- END BASELINE --> markers
#      (BEGIN must precede END).
#   3. AGENTS.md is <= 200 lines.
#   4. CLAUDE.md exists and is either:
#      - a symbolic link to AGENTS.md, or
#      - a regular file with exact content "AGENTS.md" (Windows materialized symlink).
#   5. CLAUDE.md points at AGENTS.md (directly or materialized form).
#   6. BASELINE_VERSION exists and contains a single semver line MAJOR.MINOR.PATCH.

set -u
fail() { echo "FAIL: $*" >&2; exit 1; }

# Resolve repo root: prefer git, fall back to script's parent dir.
if ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  :
else
  ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fi
cd "$ROOT" || fail "cannot cd to repo root: $ROOT"

# 1. AGENTS.md exists and is a regular file
[ -f AGENTS.md ] || fail "AGENTS.md missing or not a regular file"

# 2. baseline markers present, in order
begin_line=$(grep -n -F '<!-- BEGIN BASELINE -->' AGENTS.md | head -n1 | cut -d: -f1)
end_line=$(grep -n -F '<!-- END BASELINE -->' AGENTS.md | head -n1 | cut -d: -f1)
[ -n "$begin_line" ] || fail "AGENTS.md missing <!-- BEGIN BASELINE --> marker"
[ -n "$end_line" ] || fail "AGENTS.md missing <!-- END BASELINE --> marker"
[ "$begin_line" -lt "$end_line" ] || fail "AGENTS.md baseline markers out of order"

# 3. AGENTS.md <= 200 lines
agents_lines=$(wc -l < AGENTS.md | tr -d ' ')
[ "$agents_lines" -le 200 ] || fail "AGENTS.md has $agents_lines lines (> 200)"

# 4-5. CLAUDE.md symlink target (or Windows materialized symlink file)
if [ -L CLAUDE.md ]; then
  target=$(readlink CLAUDE.md)
  [ "$target" = "AGENTS.md" ] || fail "CLAUDE.md points at '$target', expected 'AGENTS.md'"
  claude_ref="CLAUDE.md -> AGENTS.md"
elif [ -f CLAUDE.md ]; then
  target=$(tr -d '\r\n' < CLAUDE.md)
  [ "$target" = "AGENTS.md" ] || fail "CLAUDE.md file content is '$target', expected 'AGENTS.md'"
  claude_ref="CLAUDE.md materialized as file content 'AGENTS.md'"
else
  fail "CLAUDE.md missing (expected symlink to AGENTS.md or materialized file)"
fi

# 6. BASELINE_VERSION exists and is EXACTLY one line containing a
# MAJOR.MINOR.PATCH semver, optionally followed by a single trailing
# newline. Use `wc -l` (counts newlines) so a file like "0.1.0\n\n" is
# rejected — a stray blank line would otherwise be allowed by a
# non-blank-only check. This keeps the file's role as the canonical
# single-source-of-truth version unambiguous.
[ -f BASELINE_VERSION ] || fail "BASELINE_VERSION missing"
line_count=$(wc -l < BASELINE_VERSION | tr -d ' ')
[ "$line_count" -eq 1 ] \
  || fail "BASELINE_VERSION must be exactly one line plus trailing newline (got $line_count newlines)"
ver=$(tr -d ' \t\r\n' < BASELINE_VERSION)
echo "$ver" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' \
  || fail "BASELINE_VERSION must contain MAJOR.MINOR.PATCH (got '$ver')"

echo "OK: AGENTS.md ($agents_lines lines), $claude_ref, BASELINE_VERSION=$ver"
