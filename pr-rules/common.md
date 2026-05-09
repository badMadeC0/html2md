# pr-rules/common.md — Cross-stack PR review rules

These rules apply to every pull request regardless of language. Stack-specific
rules layer on top in `pr-rules/<lang>.md` and `pr-rules/service-*.md`.

## 1. AI-assistance disclosure

- Every PR authored or substantially edited by an AI agent MUST have a title
  starting with `[AI-Assisted]`.
- The PR body MUST include a link to the originating Claude chat (or other
  agent transcript). The placeholder `<CLAUDE_CHAT_URL>` is acceptable in
  draft PRs; CI may warn during draft PR checks if it remains unfilled, but
  once the PR is ready for review, CI will fail until the placeholder is
  replaced with the actual link.
- Reviewers should not approve an AI-authored or substantially AI-edited PR
  that lacks the tag or the required link.

## 2. Scope discipline

- One PR = one purpose. Do not bundle drive-by refactors with feature work.
- No edits outside the declared scope of the PR description.
- Do not introduce new runtime, build, or CI dependencies without an explicit
  note in the PR body and reviewer sign-off.
- Do not add commented-out code, "TODO" placeholders without an issue link,
  or speculative abstractions for hypothetical future requirements.

## 3. Secrets and sensitive files

- Never read, write, edit, or commit: `.env*`, `*.pem`, `*.key`,
  `credentials.json`, `*.crt`, `id_rsa*`, or any file matching a sensible
  "secret" naming convention.
- Never paste credentials into PR bodies, comments, or test fixtures.
- The Claude Code hook `.claude/hooks/protect-sensitive-files.py` blocks
  Edit/Write to these paths. If the hook fires on a legitimate file, name
  the file differently rather than disabling the hook.

## 4. Destructive and shared-state operations

- Never run `git push --force`, `git reset --hard` against shared branches,
  or any command that rewrites public history.
- Never run `gh pr merge`, `gh pr close`, or trigger a deploy from an AI
  agent. These require explicit human action.
- Never delete files, branches, or workflow configuration as a shortcut to
  make a check pass; investigate the root cause instead.

## 5. Tests

- New code paths require new tests. Smoke tests at minimum.
- All existing tests must remain green. Do not skip or `xfail` tests to
  silence failures unrelated to the PR.
- Tests must not depend on external network calls unless explicitly marked.

## 6. Copyright

- Do not paste large verbatim chunks of third-party content (>20 words) into
  source files, docs, or PRs.
- Never reproduce song lyrics or other clearly copyrighted creative content.

## 7. Edge cases

- When an agent encounters an ambiguous situation that is not covered by any
  rule above, append a row to `pr-rules/edge-cases.md` describing the
  situation, the decision taken, and the rationale. Never delete rows.

## 8. PR template

- The PR description must follow `.github/PULL_REQUEST_TEMPLATE.md`. Empty
  checkboxes are a request for re-review.
