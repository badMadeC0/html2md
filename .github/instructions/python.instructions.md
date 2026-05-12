---
applyTo: "**/*.py,**/pyproject.toml"
---

# Python instructions (path-scoped, loaded for *.py and pyproject.toml)

Authoritative source: [`pr-rules/python.md`](../../pr-rules/python.md).
Repo-local overrides: [`pr-rules/python.local.md`](../../pr-rules/python.local.md).

## Required practices

- **Python 3.8 floor.** No syntax/APIs added after 3.8: no `match`/`case`,
  no `str.removeprefix` / `removesuffix`, no `tomllib`, no `typing.Self`,
  no PEP 695 generic syntax.
- New or modified modules SHOULD start with `from __future__ import annotations`.
- Entry-point function signature: `main(argv=None) -> int`.
- CLI parsing: `argparse.ArgumentParser` only. No click/typer/fire.
- Filesystem: `pathlib.Path`. Always pass `encoding="utf-8"` on `open()`
  and `Path.open()`.
- Imports grouped stdlib → third-party → local with one blank line between
  groups. No `;`-chained statements.

## Dependencies

- Runtime deps: `pyproject.toml` `[project.dependencies]`. Adding one
  requires explicit reviewer sign-off in the PR body.
- Allowed runtime set today: `markdownify`, `beautifulsoup4`, `requests`,
  `reportlab`, `pillow`, `pyyaml`, `anthropic`. Optional `deploy` extra
  adds `flask`, `gunicorn`.

## Tests

- pytest only (no `unittest.TestCase` for new tests).
- Smoke test = `subprocess.run` that asserts `--help` exits 0.
- New entry points or CLI utilities must ship with a smoke test.

## Cross-platform

- CI runs on `windows-latest`. No Unix-only assumptions in tested code
  paths (no Unix signals, no `/tmp/...` literals, no shebang-only entry).

## Service-specific

- `src/html2md/cli.py` is the active in-repo runtime for URL fetching and
  HTML→Markdown conversion. Keep changes backward-compatible
  (`main(argv=None) -> int` signature, existing CLI flags, default field
  set used by `html2md-log-export`). Architectural changes (new
  dependencies, output formats, packaging boundary) belong in a dedicated
  PR with an ADR. See
  [`pr-rules/service-html2md.md`](../../pr-rules/service-html2md.md).
