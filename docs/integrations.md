# Integrations

> Skeleton — populate as integrations are added.

External systems this repo talks to.

| System | Direction | Auth | Used by | Notes |
| ------ | --------- | ---- | ------- | ----- |
|        |           |      |         |       |

## Conventions

- Live network calls are forbidden in the test suite. URL-fetching code
  paths exercise local fixtures or stub HTTP servers. (See
  `pr-rules/service-html2md.md` §5.)
- Credentials are never read from `.env*` or `credentials.json` by the
  test suite. The Claude Code hook
  `.claude/hooks/protect-sensitive-files.py` blocks accidental writes.
