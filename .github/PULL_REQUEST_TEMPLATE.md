<!--
  Title format: [AI-Assisted] <imperative summary>. Required by
  .github/workflows/ai-assisted-pr-guard.yml.
-->

## Summary

<!-- 1–3 sentences. What changes and why. -->

## Originating Claude chat

<CLAUDE_CHAT_URL>

<!--
  Replace the placeholder above with the chat URL (claude.ai/chat/...,
  cursor, codex, jules — whatever drove this PR). Required for any PR
  whose title starts with [AI-Assisted].
-->

## Scope

- [ ] One PR, one purpose. No drive-by refactors.
- [ ] No edits outside the declared scope.
- [ ] No new runtime, build, or CI dependencies (or — if any — listed and justified below).

## Tests

- [ ] `pytest -q` passes locally.
- [ ] `scripts/check_agents_consistency.sh` passes.
- [ ] New code paths have at least a smoke test.

## Baseline rules

- [ ] PR follows `pr-rules/common.md` and `pr-rules/python.md`.
- [ ] Service-specific rules (`pr-rules/service-html2md.md`) reviewed.
- [ ] If an ambiguity surfaced, an entry was appended to
      `pr-rules/edge-cases.md`.

## Sensitive files

- [ ] No `.env*`, `*.pem`, `*.key`, `credentials.json`, `*.crt`, or
      `id_rsa*` files were created, modified, or pasted into the diff.

## Notes for reviewers

<!-- Anything reviewers need to know. Risk areas, follow-ups, etc. -->
