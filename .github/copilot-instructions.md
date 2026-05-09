# Copilot custom instructions — html2md-cli

This file is a thin pointer. Authoritative guidance lives in
[`AGENTS.md`](../AGENTS.md) and the rule sets under [`pr-rules/`](../pr-rules/).

## Read first

1. [`AGENTS.md`](../AGENTS.md) — baseline and project context.
2. [`pr-rules/common.md`](../pr-rules/common.md) — cross-stack rules.
3. [`pr-rules/python.md`](../pr-rules/python.md) — Python rules
   (also mirrored as `.github/instructions/python.instructions.md` for
   path-scoped Copilot loading).
4. [`pr-rules/python.local.md`](../pr-rules/python.local.md) — repo-local
   Python overrides (currently empty).
5. [`pr-rules/service-html2md.md`](../pr-rules/service-html2md.md) —
   service-specific rules (placeholder `cli.py`, JSONL log-export contract,
   Windows CI runner, symlinked `CLAUDE.md`).

## Hard rules

- Never push, open, merge, or close PRs.
- Never read or write `.env*`, `*.pem`, `*.key`, `credentials.json`,
  `*.crt`, `id_rsa*`, or any file matching a sensible secret naming
  convention (e.g., `secrets.*`, `secret.*`, `*.secret.*`, `*.secrets.*`,
  `*api-token*`, `*-credentials.*`). See
  [`pr-rules/common.md`](../pr-rules/common.md) §3 for the canonical list.
  The hook `.claude/hooks/protect-sensitive-files.py` enforces this for
  Edit/Write.
- Every AI-assisted PR title must start with `[AI-Assisted]`. The body must
  link to the originating Claude / agent chat URL.
- Append edge cases to [`pr-rules/edge-cases.md`](../pr-rules/edge-cases.md);
  never delete rows.

## Quick checklist before suggesting code

- Python 3.8 compatible? (no `match`, no `tomllib`, no `removeprefix`).
- `from __future__ import annotations` present in new modules?
- Entry-point signature `main(argv=None) -> int`?
- `pathlib.Path` and explicit `encoding="utf-8"`?
- No new runtime / build dependencies in `pyproject.toml`?
- For new CLI utilities: a smoke test that asserts `--help` exits 0?
- For changes to `src/html2md/cli.py`: still a placeholder, no real
  conversion logic added?

## Review prompt

The detailed review workflow lives in
[`.github/prompts/review-pr.prompt.md`](prompts/review-pr.prompt.md).
