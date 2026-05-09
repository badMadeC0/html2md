
# html2md-cli (0.11.6) — Repository Snapshot

This repository contains the current source snapshot: a placeholder `html2md` CLI entry point, a working JSONL→CSV log export utility, Windows helper scripts, tests, and documentation.

## Purpose

This repo currently provides:

- A placeholder `html2md` CLI command that exposes parser/help behavior (`--help`/`--help-only`) and prints a runtime availability message.
- A functional `html2md-log-export` utility for exporting JSONL logs to CSV.

The full runtime conversion workflow described in earlier packaging notes is **not embedded in this source tree**.

## Tech Stack

- **Language:** Python 3.8+
- **Build:** setuptools + wheel via `pyproject.toml` (PEP 517/518)
- **Core dependencies:** [`markdownify`](https://pypi.org/project/markdownify/), [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/), [`requests`](https://pypi.org/project/requests/), [`reportlab`](https://pypi.org/project/reportlab/), [`pillow`](https://pypi.org/project/Pillow/), [`pyyaml`](https://pypi.org/project/PyYAML/)
- **Testing:** pytest
- **CI:** GitHub Actions (Windows-latest)
- **Platform extras:** PowerShell setup scripts + WPF GUI for Windows

## Entry Points

| Entry Point | Target | Description |
| --- | --- | --- |
| `html2md` | [`src/html2md/cli.py:main`](src/html2md/cli.py) | Primary CLI |
| `html2md-log-export` | [`src/html2md/log_export.py:main`](src/html2md/log_export.py) | JSONL-to-CSV log export utility |
| `python -m html2md` | [`src/html2md/__main__.py`](src/html2md/__main__.py) | Module execution, delegates to `cli.main()` |

## Key Files

| File | Description |
| --- | --- |
| [`src/html2md/cli.py`](src/html2md/cli.py) | Main CLI module |
| [`src/html2md/log_export.py`](src/html2md/log_export.py) | Reads JSONL logs and exports selected fields to CSV |
| [`src/html2md/__init__.py`](src/html2md/__init__.py) | Package init, exposes `__version__` |
| [`tests/test_cli_smoke.py`](tests/test_cli_smoke.py) | Smoke test verifying `--help` exits cleanly |
| [`setup-html2md.ps1`](setup-html2md.ps1) | Windows PowerShell setup (venv, deps, PATH) |
| [`gui-url-convert.ps1`](gui-url-convert.ps1) | Windows WPF GUI for URL conversion |
| [`run-html2md.bat`](run-html2md.bat) | Windows batch launcher |
| [`run-gui.bat`](run-gui.bat) | Windows GUI launcher |

## Features in this repository

- `html2md` CLI placeholder command (`--help` and `--help-only` parsing)
- JSONL-based log export to CSV via `html2md-log-export`
- Package/module entry points and smoke tests
- Windows bootstrap and launcher scripts (PowerShell + batch)

## Working with AI agents

This repo follows the [AI-PR-Review baseline](AGENTS.md). Before any AI
agent (Claude, Cursor, Copilot, Codex, Jules, Gemini Code Assist) proposes
a change, it should read:

- [`AGENTS.md`](AGENTS.md) — authoritative guidance. `CLAUDE.md` is a symlink to this file.
- [`pr-rules/`](pr-rules/) — review rule sets (`common.md`, `python.md`, `service-html2md.md`, plus the append-only `edge-cases.md` ledger). Treat these as review guidance, and cross-check any architecture or runtime-boundary claims against the current source tree before relying on them.
- [`adr/`](adr/) — architecture decision records; use these together with the current codebase to confirm how the repository is actually structured.

PR conventions:

- AI-assisted PRs should start with `[AI-Assisted]` and include the originating agent transcript URL in the body (for example, Claude, Cursor, Codex, or Jules). The workflow [`.github/workflows/ai-assisted-pr-guard.yml`](.github/workflows/ai-assisted-pr-guard.yml) currently enforces the transcript-link requirement only for PRs whose titles already include `[AI-Assisted]`.
- The Claude slash command [`/review-pr`](.claude/commands/review-pr.md) walks an open PR against the rule sets.
- Run [`scripts/check_agents_consistency.sh`](scripts/check_agents_consistency.sh) before opening a PR.
