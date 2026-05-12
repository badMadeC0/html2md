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

1. Run `gh pr view --json number,title,body,headRefName,baseRefName,isDraft`
   and capture title, body, baseRefName, and isDraft. Then:
   - If the title starts with `[AI-Assisted]`, confirm the body contains
     an originating agent transcript URL from one of the accepted forms
     (matches `.github/workflows/ai-assisted-pr-guard.yml` and
     `pr-rules/common.md`):
     - `https://claude.ai/chat/<id>`
     - `https://claude.ai/share/<id>`
     - `https://claude.ai/code/session_<id>`
     - `https://cursor.com/share/<id>`
     - `https://chatgpt.com/codex/<id>`
     - `https://jules.google.com/task/<id>`
     If the body still contains the literal placeholder
     `<CLAUDE_CHAT_URL>`, flag it as a violation ONLY when `isDraft` is
     false. Drafts may keep the placeholder while the transcript is not
     ready yet.
   - If the title does not start with `[AI-Assisted]`, treat the PR as
     non-AI-authored for this check and do not report the missing marker
     or missing transcript URL as a violation.
2. Enumerate changed files via `git diff --name-only origin/${baseRefName}...HEAD`
   using the `baseRefName` captured above (the PR may target a release
   branch, not `main`). If `origin/${baseRefName}` is missing locally,
   fall back to `gh pr diff <number> --name-only`.
3. Read `pr-rules/common.md`. For each rule, scan the diff and the changed
   files for violations. Report each violation as:
   `path:line — rule N from <ruleset>: <one-line summary>`.
4. If any changed file matches `*.py` OR is `pyproject.toml`, repeat
   step 3 for `pr-rules/python.md` then `pr-rules/python.local.md`.
   The Python rules apply to packaging metadata as well as source.
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
