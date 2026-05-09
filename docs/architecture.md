# Architecture

> Skeleton — populate as the project evolves.

## High-level diagram

<!--
  Replace with a text-mode or mermaid diagram. Suggested first version:
  user → html2md (CLI) → packaged-runtime → output (md|pdf|txt)
                       ↘ html2md-log-export (CLI) → CSV
                       ↘ html2md-upload (CLI) → S3 / etc.
-->

## Modules

| Module | Path | Responsibility |
| ------ | ---- | -------------- |
| `cli` | `src/html2md/cli.py` | CLI entry point for fetching HTML inputs and converting them to output formats. |
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
