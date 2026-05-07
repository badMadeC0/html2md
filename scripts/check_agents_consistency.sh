#!/usr/bin/env bash
# scripts/check_agents_consistency.sh
# Verifies the AI-PR-Review baseline structure is well-formed.
# Exits 0 on success; non-zero with a diagnostic on the first failure.
#
# Checks:
#   1. AGENTS.md exists and is a regular file.
#   2. AGENTS.md contains <!-- BEGIN BASELINE --> and <!-- END BASELINE --> markers
#      (BEGIN must precede END).
#   3. AGENTS.md is <= 80 lines.
#   4. CLAUDE.md exists and is a symbolic link.
#   5. CLAUDE.md points at AGENTS.md (relative target literally "AGENTS.md").
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

# 3. AGENTS.md <= 80 lines
agents_lines=$(wc -l < AGENTS.md | tr -d ' ')
[ "$agents_lines" -le 80 ] || fail "AGENTS.md has $agents_lines lines (> 80)"

# 4. CLAUDE.md is a symlink
[ -L CLAUDE.md ] || fail "CLAUDE.md must be a symbolic link"

# 5. CLAUDE.md points at AGENTS.md
target=$(readlink CLAUDE.md)
[ "$target" = "AGENTS.md" ] || fail "CLAUDE.md points at '$target', expected 'AGENTS.md'"

# 6. BASELINE_VERSION exists and is a valid semver line
[ -f BASELINE_VERSION ] || fail "BASELINE_VERSION missing"
ver=$(tr -d ' \t\n\r' < BASELINE_VERSION)
echo "$ver" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$' \
  || fail "BASELINE_VERSION must contain MAJOR.MINOR.PATCH (got '$ver')"

echo "OK: AGENTS.md ($agents_lines lines), CLAUDE.md -> AGENTS.md, BASELINE_VERSION=$ver"
