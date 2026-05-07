# pr-rules/python.md — Python-specific PR review rules

These rules layer on top of `pr-rules/common.md` for any PR that touches
Python code (`*.py`, `pyproject.toml`, anything under `src/` or `tests/`).
Repo-local overrides go in `pr-rules/python.local.md` (loaded after this).

## 1. Language version

- Python **>= 3.8** is the supported floor.
- Do not use syntax or stdlib APIs added after 3.8: no `match`/`case`,
  no `str.removeprefix` / `str.removesuffix`, no `tomllib`, no
  `typing.Self`, no PEP 695 generic syntax.
- New or modified modules SHOULD include `from __future__ import annotations`
  at the top.

## 2. Style and idioms

- Entry-point functions follow the signature `main(argv=None) -> int` so
  they work both as CLI commands (via `[project.scripts]` in
  `pyproject.toml`) and inside tests.
- Use `argparse.ArgumentParser` for CLI parsing — no click, typer, fire,
  or other frameworks.
- Use `pathlib.Path` for filesystem operations — no `os.path` joins, no
  string concatenation of path components.
- Pass `encoding="utf-8"` explicitly on every `open()` and `Path.open()`.
- Group imports as stdlib → third-party → local with one blank line
  between groups.
- One responsibility per line. Don't pack unrelated statements with `;`.

## 3. Dependencies

- Runtime deps live in `pyproject.toml` `[project.dependencies]`. Build-system
  deps live in `[build-system].requires`. Don't add a dep without raising it
  in the PR body.
- Common dev tools that are NOT declared as deps: `pytest`, `build`. Treat
  them as optional locals.
- The current runtime set: `markdownify`, `beautifulsoup4`, `requests`,
  `reportlab`, `pillow`, `pyyaml`, `anthropic`. The optional `deploy`
  extra adds `flask`, `gunicorn`.

## 4. Layout

- Source lives under `src/html2md/` (src layout).
- Tests live under `tests/` and run with `pytest -q`.
- Build config is entirely in `pyproject.toml`. Do not introduce
  `setup.py` or `setup.cfg`.

## 5. Testing

- All tests use **pytest**; no `unittest` subclasses for new tests.
- Smoke tests for CLI commands shell out via `subprocess.run` and assert on
  return codes.
- Every new entry point or utility needs at least a smoke test that
  verifies `--help` exits 0.
- Do not import internal modules from a CLI smoke test when the intent is
  to verify the CLI surface — drive it via `subprocess`.

## 6. Security

- No `subprocess` calls with `shell=True` and unsanitized user input.
- Validate and sanitize file paths from user input. Reject `..` traversal
  outside the intended root.
- Never log secrets or full request bodies that may contain credentials.

## 7. Cross-platform / CI compatibility

- CI runs on `windows-latest`. Avoid Unix-only assumptions:
  - no `#!/usr/bin/env python` shebangs as the only invocation path
  - no hard-coded forward-slash paths in code paths exercised on Windows
  - no Unix signals (SIGUSR1, SIGTERM handlers) in cross-platform code
- Symlinks may not resolve on Windows checkouts; do not rely on them at
  runtime.

## 8. License

- The project is MIT-licensed. Do not introduce code under incompatible
  licenses (GPL, AGPL) without an explicit ADR.
