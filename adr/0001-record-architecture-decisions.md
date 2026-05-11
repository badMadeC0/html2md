# 0001 — Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-05-06
- **Deciders:** Repo maintainers

## Context

`html2md-cli` accumulates non-trivial design choices: the in-repo
CLI/runtime boundary, the JSONL log-export field contract, the
Windows-first CI runner, the symlinked `CLAUDE.md`, and the
AI-PR-Review baseline itself. Without a written record, future
contributors (human or AI) re-litigate settled decisions or, worse,
silently reverse them.

## Decision

We will record architecturally significant decisions as Markdown files
under `adr/`, numbered sequentially (`NNNN-kebab-case-title.md`).

- New ADRs use `adr/0000-template.md` as the starting point.
- ADRs are append-only. To change a decision, write a new ADR with status
  `Accepted` and update the older ADR's `Status:` line to
  `Superseded by NNNN`.
- ADRs are referenced from the relevant `pr-rules/*.md` rule, from
  `docs/architecture.md`, and from PR descriptions when applicable.

## Consequences

- **Positive:** decisions are durable and discoverable. AI agents reading
  `pr-rules/service-html2md.md` can follow links to learn the "why".
- **Negative:** small overhead per decision. A short ADR is fine — the
  template encourages brevity.
- **Neutral / follow-ups:** the template format is MADR-flavored; we may
  trim or extend as the repo's ADR set grows.

## Alternatives considered

- **Option A — record decisions only in commit messages:** Rejected.
  Commit messages are not navigable as a coherent set, and search across
  them degrades over time.
- **Option B — record decisions in a single `DECISIONS.md`:** Rejected.
  Files grow unwieldy and merge poorly across parallel branches.

## References

- [Michael Nygard, "Documenting Architecture Decisions"](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
- [MADR template](https://adr.github.io/madr/)
