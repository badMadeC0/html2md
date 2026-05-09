# pr-rules/service-html2md.md — Service-specific PR review rules

These rules layer on top of `pr-rules/common.md` and `pr-rules/python.md`
for any PR in this repository specifically.

## 1. CLI runtime scope

- `src/html2md/cli.py` in this repository is the active runtime for URL
  fetching and HTML conversion flows.
- Keep CLI changes scoped and backward-compatible (argument parsing,
  output handling, conversion behavior, and error handling). Output format
  changes and different handling of existing edge cases should be treated
  as breaking unless explicitly approved.
- If a PR proposes a major architecture move (for example, splitting core
  conversion runtime across packages/repos), that requires an ADR under
  `adr/` first.

## 2. Log-export utility contract

- `html2md.log_export:main` reads JSONL logs and writes CSV with
  configurable field selection. Default fields:
  `ts,input,output,status,reason`.
- Changing the default field set is a breaking change for downstream
  consumers and requires a version bump in `src/html2md/__init__.py`
  plus a note in the PR body.

## 3. Windows CI is the authoritative runner

- CI runs on `windows-latest`. PRs must not assume POSIX-only behavior
  in tested code paths. PowerShell helpers in `setup-html2md.ps1` and
  `gui-url-convert.ps1` are out of pytest scope but must keep their
  shebangs / encoding intact.
- Test fixtures must use `Path` and `tempfile.TemporaryDirectory()`,
  not hard-coded `/tmp/...` paths.

## 4. CLAUDE.md is a symlink

- `CLAUDE.md` is a symbolic link to `AGENTS.md`. On Windows checkouts
  without symlink support it may render as a text file containing the
  string `AGENTS.md`. Do not "fix" this by replacing it with a copy of
  AGENTS.md content — it would diverge silently. The consistency check
  `scripts/check_agents_consistency.sh` accepts either form (symlink or
  materialized text-file target).

## 5. No runtime fetches in tests

- Tests must not perform live HTTP requests. URL-fetching code paths
  must be exercised against a local fixture (file:// URL or a stub
  HTTP server in a fixture).

## 6. Version bumps

- `src/html2md/__init__.py` (`__version__`) is the single source of truth
  for the package version. `pyproject.toml` `version` field must match.
  A version-bump PR should update both in the same commit.

## 7. Baseline sync

- Files inside `<!-- BEGIN BASELINE --> ... <!-- END BASELINE -->` markers
  in `AGENTS.md`, plus everything under `pr-rules/` (except
  `python.local.md` and `edge-cases.md`), are synced from the AI-PR-Review
  template repo. Local edits to those regions will be overwritten by
  `.github/workflows/sync-from-template.yml`.
