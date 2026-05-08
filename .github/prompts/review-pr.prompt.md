---
mode: agent
description: Review the current PR against the AI-PR-Review baseline.
---

# review-pr — GitHub Copilot prompt

Mirror of `.claude/commands/review-pr.md` for use in VS Code Copilot
prompt-file flows.

## Inputs

- The currently open PR (`gh pr view --json number,title,body`).
- Rule files: `pr-rules/common.md`, `pr-rules/python.md`,
  `pr-rules/python.local.md`, `pr-rules/service-html2md.md`,
  `pr-rules/edge-cases.md`.

## Procedure

1. Load PR title and body. Determine whether the PR is AI-authored or
   substantially AI-edited under `pr-rules/common.md`. Check:
   - If it is AI-authored or substantially AI-edited, title starts with
     `[AI-Assisted]`.
   - If it is AI-authored or substantially AI-edited, body contains a
     Claude chat URL (warn on the literal placeholder
     `<CLAUDE_CHAT_URL>`).
   - If it is not AI-authored or substantially AI-edited, do not flag the
     absence of `[AI-Assisted]` or a Claude chat URL as a violation.
2. Enumerate changed files with `git diff --name-only origin/main...HEAD`.
3. For each rule in `pr-rules/common.md`, search the diff for violations.
   Format each as `path:line — common.md rule N: <one-line summary>`.
4. If any `*.py` files changed, repeat step 3 against `pr-rules/python.md`
   then `pr-rules/python.local.md`.
5. Repeat step 3 against `pr-rules/service-html2md.md`.
6. Run `scripts/check_agents_consistency.sh`. Embed its output in the
   "Baseline consistency" section of the report.
7. Output a single Markdown report with: PR metadata, violations grouped
   by ruleset, baseline consistency, and a Green / Yellow / Red verdict.

## Constraints

- Read-only. Do not edit files; do not call `gh pr` mutations.
- Suggest edge-case rows where appropriate but do NOT append them — that
  is the `/edge-case` command's job.
