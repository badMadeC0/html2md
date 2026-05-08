# AGENTS.md

Authoritative guidance for AI coding agents (Claude, Cursor, Copilot, Codex,
Jules, Gemini Code Assist) working in this repository. `CLAUDE.md` is a
symbolic link to this file.

<!-- BEGIN BASELINE -->
## AI-PR-Review baseline

This repo follows the AI-PR-Review baseline structure. The block between
the markers is managed centrally; do not hand-edit.

- Review rules:
  - `pr-rules/common.md` — cross-stack rules (security, secrets, scope,
    `[AI-Assisted]` PR tag, copyright)
  - `pr-rules/python.md` — Python-specific rules
  - `pr-rules/python.local.md` — repo-local Python overrides
  - `pr-rules/service-html2md.md` — service-specific rules
  - `pr-rules/edge-cases.md` — append-only edge-case ledger
- Architectural decisions: `adr/` (template `adr/0000-template.md`)
- Reference docs: `docs/overview.md`, `docs/architecture.md`,
  `docs/business-rules.md`, `docs/integrations.md`, `docs/domain-model.md`
- Slash commands: `.claude/commands/review-pr.md`,
  `.claude/commands/edge-case.md`
- Sensitive-file write guard: `.claude/hooks/protect-sensitive-files.py`
- PR template: `.github/PULL_REQUEST_TEMPLATE.md`
- PR-title check: `.github/workflows/ai-assisted-pr-guard.yml` enforces
  the Claude chat link requirement for PRs marked `[AI-Assisted]`; draft
  PRs may temporarily use `<CLAUDE_CHAT_URL>` until they are ready.
- Consistency check: `scripts/check_agents_consistency.sh`
- Baseline version: `BASELINE_VERSION` (semver)

Hard rules — no AI agent may override:
1. Never push, open, merge, or close PRs without explicit human approval.
2. Never read or write `.env*`, `*.pem`, `*.key`, `credentials.json`,
   `*.crt`, `id_rsa*`. The hook above blocks Edit/Write attempts.
3. Every AI-assisted PR title MUST start with `[AI-Assisted]` and the
   body MUST include the originating Claude chat URL; draft PRs may use
   the `<CLAUDE_CHAT_URL>` placeholder until the real URL is added.
4. Append new edge cases to `pr-rules/edge-cases.md`; never delete rows.
<!-- END BASELINE -->

## Project context (html2md-cli)

- **Stack:** Python 3.8+, src-layout (`src/html2md/`), pytest, setuptools.
- **CI:** GitHub Actions on `windows-latest` (`.github/workflows/ci.yml`).
- **Entry points:** `html2md` (`cli.py:main`), `html2md-log-export`
  (`log_export.py:main`), `html2md-upload` (`upload.py:main`).
- **Status of `cli.py`:** placeholder stub — the full converter ships
  from a separate packaged build. Do not add conversion logic here.
- **Encoding:** UTF-8 everywhere; use `pathlib.Path` and `argparse`.

## How agents should work here

1. Read `pr-rules/common.md`, then `pr-rules/python.md`, then
   `pr-rules/service-html2md.md` before proposing any change.
2. Run `pytest -q` after every code edit.
3. Run `scripts/check_agents_consistency.sh` before opening a PR.
4. When in doubt, append to `pr-rules/edge-cases.md` rather than guess.
