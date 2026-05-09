# Architecture

> Skeleton — populate as the project evolves.

## High-level diagram

<!--
  Replace with a text-mode or mermaid diagram. Suggested first version:
  user → html2md (CLI; src/html2md/cli.py) → markdown output (.md)
       ↘ html2md-log-export (CLI; src/html2md/log_export.py) → CSV
       ↘ html2md-upload (CLI; src/html2md/upload.py) → upload target
  The conversion runtime is in-repo (markdownify-based). Packaged builds
  may extend it; document that here when applicable.
-->

## Modules

| Module | Path | Responsibility |
| ------ | ---- | -------------- |
| `cli` | `src/html2md/cli.py` | CLI entry point for fetching HTML inputs and running the in-repo conversion flow. |
| `log_export` | `src/html2md/log_export.py` | JSONL → CSV log exporter. |
| `upload` | `src/html2md/upload.py` | Upload entry point. |
| `app` | `src/html2md/app.py` | (describe responsibility) |
| `__main__` | `src/html2md/__main__.py` | `python -m html2md` shim. |

## Data flow

<!-- Describe the lifecycle of a request / invocation end-to-end. -->

## Operational notes

- CI: `windows-latest` GitHub Actions runner.
- Build: setuptools + wheel via `pyproject.toml` (PEP 517/518).
- Test: `pytest -q`.
