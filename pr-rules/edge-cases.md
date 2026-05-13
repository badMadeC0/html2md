# pr-rules/edge-cases.md — Append-only edge-case ledger

When an AI agent encounters an ambiguous situation that is not covered by
`pr-rules/common.md`, `pr-rules/python.md`, or `pr-rules/service-html2md.md`,
append a new row below describing the situation, the decision taken, and the
rationale. **Do not delete or rewrite existing rows** — supersede them with a
new row that references the older row's ID.

## Conventions

- ID format: `EC-NNNN` (zero-padded, monotonically increasing).
- Date format: ISO-8601 (`YYYY-MM-DD`).
- One row per edge case. Keep notes terse; link to the PR for context.

## Ledger

| ID | Date | File or area | Rule conflict / ambiguity | Decision | PR |
| -- | ---- | ------------ | ------------------------- | -------- | -- |
| EC-0001 | 2026-05-13 | `.github/workflows/ai-assisted-pr-guard.yml` | PR created by Jules contains a `jules.google.com/task/…` transcript URL in the body but the PR title was not prefixed with `[AI-Assisted]`, causing `check-ai-assisted-marker` to fail | Prefix the PR title with `[AI-Assisted]` to satisfy the guard; never strip the transcript URL from the body as that would remove required AI attribution | #1050 |
