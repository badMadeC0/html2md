# Copilot Custom Instructions

## Project Context

html2md-cli is a Python CLI tool that converts HTML to Markdown, PDF, and TXT formats. The CLI module (`src/html2md/cli.py`) is a **placeholder stub** — the full runtime ships via a separate packaged build. Do not attempt to implement conversion logic in this repository.

## Language & Runtime

- Python **>= 3.8** — do not use syntax or stdlib features added after 3.8 (e.g., `match` statements, `str.removeprefix`, `tomllib`).
- Always include `from __future__ import annotations` at the top of every module.

## Code Style

- Entry-point functions must follow the signature `main(argv=None)` so they work both as CLI commands and in tests.
- Use `argparse.ArgumentParser` for CLI argument parsing — no click, typer, or other frameworks.
- Use `pathlib.Path` for all filesystem operations — never raw `os.path` calls.
- Use `encoding='utf-8'` explicitly on all `open()` / `Path.open()` calls.
- Keep imports grouped: stdlib, third-party, local — one blank line between groups.
- Prefer concise code, but avoid packing unrelated statements on one line.

## Dependencies

Runtime dependencies are locked in `pyproject.toml`. Do not add new runtime dependencies without discussion. The current set is:
- `markdownify`, `beautifulsoup4`, `requests`, `reportlab`, `pillow`, `pyyaml`

Dev dependencies: `pytest`, `setuptools`, `wheel`, `build`.

## Project Layout

- Source lives under `src/html2md/` (PEP 517 src-layout).
- Tests live under `tests/` and run with `pytest -q`.
- Build config is entirely in `pyproject.toml` — there is no `setup.py` or `setup.cfg`.
- Windows integration scripts (`*.bat`, `*.ps1`) are not part of the Python package.

## Testing

- All tests use **pytest** (no unittest subclasses).
- Smoke tests call CLI entry points via `subprocess.run` and assert on return codes.
- When adding a new module or entry point, add at least a smoke test that verifies `--help` exits 0.
- Never import internal modules directly in tests when the intent is to test the CLI interface — use subprocess.

## Review Guidance

When reviewing pull requests, pay attention to:

1. **Python 3.8 compatibility** — flag any use of newer syntax or APIs.
2. **No new runtime dependencies** unless explicitly justified.
3. **Placeholder boundary** — changes to `cli.py` should not add real conversion logic; that belongs in the packaged build.
4. **Encoding** — all file I/O must specify `encoding='utf-8'`.
5. **Path handling** — use `pathlib.Path`, not string concatenation or `os.path`.
6. **Entry-point contract** — `main(argv=None)` signature, returns an int exit code.
7. **Test coverage** — new entry points or utilities need at least a smoke test.
8. **Security** — watch for command injection in subprocess calls (no unsanitized user input in `shell=True`), and validate/sanitize file paths from user input.
9. **CI compatibility** — CI runs on `windows-latest`; avoid Unix-only assumptions (shebangs, forward-slash-only paths, Unix signals).
10. **License** — project is MIT; do not introduce code with incompatible licenses.
