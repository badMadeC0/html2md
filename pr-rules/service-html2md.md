# pr-rules/service-html2md.md — Service-specific PR review rules

These rules layer on top of `pr-rules/common.md` and `pr-rules/python.md`
for any PR in this repository specifically.

## 1. CLI placeholder boundary

- `src/html2md/cli.py` is a **placeholder stub**. The full HTML→Markdown /
  PDF / TXT conversion runtime ships from a separate packaged build.
- Do **not** add real conversion logic, URL fetching, rate-limiting, or
  ReportLab rendering to `cli.py` here. Bug fixes to argument parsing and
  help output are fine.
- If a PR proposes pulling the full runtime into this repo, that requires
  an ADR under `adr/` first.

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
  `scripts/check_agents_consistency.sh` enforces the symlink.

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
