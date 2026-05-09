---
description: Review the current branch's PR against the AI-PR-Review baseline rules.
allowed-tools: Bash, Read, Grep, Glob
---

# /review-pr — AI-PR-Review baseline review

Walk the diff between the current branch and `main` and report violations of
the baseline rule set. Read-only — do not edit files.

## Inputs

- The current branch (assume `gh pr view --json number,title,body` works).
- `pr-rules/common.md`, `pr-rules/python.md`, `pr-rules/python.local.md`,
  `pr-rules/service-html2md.md`, `pr-rules/edge-cases.md`.

## Steps

1. Run `gh pr view --json number,title,body,headRefName,baseRefName` and
   capture the title and body. Then:
   - If the title starts with `[AI-Assisted]`, confirm the body contains an
     originating agent transcript URL accepted by the guard workflow, such as
     `claude.ai/chat/...`, `claude.ai/share/...`,
     `claude.ai/code/session_...`, `cursor.com/share/...`,
     `chatgpt.com/codex/...`, or `jules.google.com/task/...`; flag the
     literal placeholder `<CLAUDE_CHAT_URL>` if still present.
   - If the title does not start with `[AI-Assisted]`, treat the PR as
     non-AI-authored for this check and do not report the missing marker or
     missing agent transcript URL as a violation.
2. Run `git diff --name-only origin/main...HEAD` to enumerate changed files.
3. Read `pr-rules/common.md`. For each rule, scan the diff and the changed
   files for violations. Report each violation as:
   `path:line — rule N from <ruleset>: <one-line summary>`.
4. If any changed file matches `*.py`, repeat step 3 for `pr-rules/python.md`
   then `pr-rules/python.local.md`.
5. Repeat step 3 for `pr-rules/service-html2md.md`.
6. Run `scripts/check_agents_consistency.sh`. If non-zero, copy its output
   into the report under "Baseline consistency".
7. Summarize at the end:
   - Green / Yellow / Red overall verdict.
   - Count of violations by rule set.
   - Any edge case worth recording (suggest a draft row for
     `pr-rules/edge-cases.md`, but do NOT write it — that's `/edge-case`).

## Output

A single Markdown report. No file edits. No `gh pr` mutations.
