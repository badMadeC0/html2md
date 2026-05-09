# Codex prompt: review-pr

Same intent as the Claude `/review-pr` command in
`.claude/commands/review-pr.md` and the Cursor `99-review-pr-skill.mdc`
rule. Use whichever invocation Codex CLI supports for prompt files.

## Inputs

- Current branch (PR open against `main`).
- Rule sets:
  - `pr-rules/common.md` (always)
  - `pr-rules/python.md` and `pr-rules/python.local.md` (if any `*.py` files changed)
  - `pr-rules/service-html2md.md` (always — service-specific)
  - `pr-rules/edge-cases.md` (consult to avoid duplicate edge cases)

## Steps

1. Read PR title and body via `gh pr view --json number,title,body`.
   - If the PR is AI-authored or substantially AI-edited, the title MUST
     start with `[AI-Assisted]`; otherwise, do not require or report that
     marker.
   - If the PR is AI-authored or substantially AI-edited, the body MUST
     contain an originating agent transcript URL with the `https://` scheme
     in one of the accepted forms (matching the guard workflow):
     `https://claude.ai/chat/<id>`, `https://claude.ai/share/<id>`,
     `https://claude.ai/code/session_<id>`,
     `https://cursor.com/share/<id>`,
     `https://chatgpt.com/codex/<id>`, or
     `https://jules.google.com/task/<id>`. Warn on the literal
     placeholder `<CLAUDE_CHAT_URL>`. For non-AI PRs, do NOT report
     the missing transcript link as a violation.
2. List changed files via `git diff --name-only origin/main...HEAD`.
3. Read each rule file in order; for every rule, scan the diff and the
   changed files for violations. Format violations as:
   `path:line — <ruleset> rule N: <one-line summary>`.
4. Run `scripts/check_agents_consistency.sh`; capture its output into the
   "Baseline consistency" section.
5. Output a Markdown report with:
   - PR metadata block (title, body link, branch).
   - Violations grouped by ruleset.
   - Baseline-consistency status.
   - Verdict: GREEN / YELLOW / RED.
   - Suggested edge-case row(s) (do not append; suggest only).

## Constraints

- Read-only. Do not edit files. Do not perform `gh pr` mutations.
- Do not call out to external services beyond `gh` and `git`.
