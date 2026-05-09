<!--
  If this PR was AI-assisted, use the title format
  [AI-Assisted] <imperative summary>. The workflow
  .github/workflows/ai-assisted-pr-guard.yml uses that prefix to enforce
  the transcript link requirement below.
-->

## Summary

<!-- 1–3 sentences. What changes and why. -->

<!--
  AI-assisted PRs only (title starts with [AI-Assisted]): add a section
  named "Originating agent transcript" with the real transcript URL on
  its own line. The URL must include the scheme (https://). Accepted forms:
      https://claude.ai/chat/<id>
      https://claude.ai/share/<id>
      https://claude.ai/code/session_<id>
      https://cursor.com/share/<id>
      https://chatgpt.com/codex/<id>
      https://jules.google.com/task/<id>
  Human-authored PRs: omit that section entirely — do NOT include the
  literal string "<" + "CLAUDE_CHAT_URL" + ">" in your body, because the
  ai-assisted-pr-guard workflow treats it as AI-assistance metadata.
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
      SSH private-key files (`id_rsa*`, `id_ed25519*`, `id_ecdsa*`,
      `id_dsa*`) were created, modified, or pasted into the diff.
- [ ] No files matching common secret naming conventions
      (e.g., `secrets.{json,yaml,yml}`, `*.secret.*`, `*.secrets.*`,
      `*api-token*`, `*-credentials.*`) were created, modified, or
      pasted into the diff. See `pr-rules/common.md` §3 for the full
      canonical list.

## Notes for reviewers

<!-- Anything reviewers need to know. Risk areas, follow-ups, etc. -->
