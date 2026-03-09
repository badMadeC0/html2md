#!/bin/bash
# Script to close invalid/redundant PRs on badMadeC0/html2md
# Run locally where you have `gh auth login` configured
# Usage: bash close-invalid-prs.sh
# Script to close invalid/redundant PRs on badMadeC0/html2md
# Run locally where you have `gh auth login` configured
# Usage: bash close-invalid-prs.sh
set -euo pipefail
# Last reviewed: 2026-03-09
# Remaining open PRs reviewed and categorized below.

REPO="badMadeC0/html2md"

# ============================================================
# NEWLY IDENTIFIED INVALID PRs (from 2026-03-09 review)
# ============================================================

# PR #311 - "Replace custom Claude agent script with official GitHub Action"
# INVALID: Diff does not match description. Only adds a stray pr-review-134.md file.
echo "Closing PR #311 (diff doesn't match description)"
gh pr close 311 --repo "$REPO" --comment "Closing: The PR diff does not match the description. It only adds a stray review file instead of the claimed workflow changes."

# PR #308 - "Bolt: [performance improvement] Hoist lookups in log export hot loop"
# INVALID: Unnecessary micro-optimization for a CLI log export tool. Adds unrelated .jules/ docs.
echo "Closing PR #308 (unnecessary micro-optimization)"
gh pr close 308 --repo "$REPO" --comment "Closing: Unnecessary micro-optimization. The log export loop is not a performance-critical hot path for a CLI tool, and the PR adds unrelated documentation files."

# PR #302 - "[AI-Assisted] Add Python-based self-healing CI workflow"
# INVALID: Over-engineered; introduces black (not used by project); adds unnecessary complexity.
echo "Closing PR #302 (over-engineered, uses tools not in project)"
gh pr close 302 --repo "$REPO" --comment "Closing: Over-engineered self-healing CI that introduces tools (\`black\`) not used by this project. Adds unnecessary complexity."

# PR #238 - "Sentinel: [HIGH] Fix XSS in Markdown Conversion"
# INVALID: CLI outputs Markdown (plain text), not browser-rendered HTML. XSS is not a real
# vulnerability here. The blacklist-based sanitizer is also critically flawed.
echo "Closing PR #238 (fabricated vulnerability)"
gh pr close 238 --repo "$REPO" --comment "Closing: This CLI tool outputs Markdown (plain text), not HTML rendered in a browser. XSS is not a real vulnerability in this context. The proposed blacklist-based sanitizer is also critically flawed and vulnerable to bypasses."

# PR #214 - "[code health] Replace bare except with specific JSONDecodeError"
# INVALID: Already fixed. log_export.py already uses 'except json.JSONDecodeError' and
# has isinstance(rec, dict) validation.
echo "Closing PR #214 (already fixed in codebase)"
gh pr close 214 --repo "$REPO" --comment "Closing: The fix is already implemented. \`log_export.py\` already uses \`except json.JSONDecodeError\` (not a bare except) and has \`isinstance(rec, dict)\` validation."

# PR #213 - "Add unit tests for log_export.main"
# INVALID: tests/test_log_export.py already exists in the codebase.
echo "Closing PR #213 (duplicate test file)"
gh pr close 213 --repo "$REPO" --comment "Closing: Duplicate — \`tests/test_log_export.py\` already exists in the codebase with test coverage for the log export utility."

# PR #140 - "Add comprehensive unit tests for sanitize_csv_field"
# INVALID: References non-existent function 'sanitize_csv_field' (actual: '_sanitize_formula').
# Overlaps with existing tests/test_csv_security.py.
echo "Closing PR #140 (references non-existent function)"
gh pr close 140 --repo "$REPO" --comment "Closing: References a non-existent function \`sanitize_csv_field\` (the actual function is \`_sanitize_formula\`). Also overlaps with existing \`tests/test_csv_security.py\`."

echo ""
echo "=== KEPT OPEN (valid PRs) ==="
echo "PR #307 - Path Traversal and scheme validation fix (real security issue in cli.py)"
echo "PR #306 - Dynamic Convert Button and Keyboard Nav (valid GUI UX improvements)"
echo "PR #301 - Grant id-token: write to claude-agent workflow (real CI fix)"
echo "PR #288 - Optimize batch URL processing with ThreadPoolExecutor (real optimization)"
echo "PR #287 - Fix Terminal Injection in CLI exception output (real security fix)"
echo "PR #194 - Optimize upload_file by reusing Anthropic client (real optimization)"
echo "PR #193 - Extract User-Agent and headers to constants (valid refactor)"
echo "PR #189 - Redact credentials from logs (real security concern)"
echo "PR #154 - Add comprehensive tests for html2md.upload (real test coverage gap)"
echo "PR #144 - Unify Duplicate Default Port Constant (real code smell in app.py)"
echo ""
echo "Done! Closed 7 invalid PRs, kept 10 valid PRs open for review."
