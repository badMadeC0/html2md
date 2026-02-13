
# html2md-cli (0.11.6) — Complete Package

This archive contains the **complete product**: runtime CLI, Windows setup+launcher, GUI, tests, and ML documentation.

## Purpose

A Python CLI tool that converts HTML to Markdown, PDF, and TXT formats. It supports fetching pages by URL with features like per-domain rate limiting, robots.txt compliance, retry/backoff, and JSONL logging with CSV export.

## Tech Stack

- **Language:** Python 3.8+
- **Build:** setuptools + wheel via `pyproject.toml` (PEP 517/518)
- **Core dependencies:** [`markdownify`](https://pypi.org/project/markdownify/), [`beautifulsoup4`](https://pypi.org/project/beautifulsoup4/), [`requests`](https://pypi.org/project/requests/), [`reportlab`](https://pypi.org/project/reportlab/), [`pillow`](https://pypi.org/project/Pillow/), [`pyyaml`](https://pypi.org/project/PyYAML/)
- **Testing:** pytest
- **CI:** GitHub Actions (Windows-latest)
- **Platform extras:** PowerShell setup scripts + WPF GUI for Windows

## Entry Points

| Entry Point | Target | Description |
|---|---|---|
| `html2md` | [`src/html2md/cli.py:main`](src/html2md/cli.py) | Primary CLI |
| `html2md-log-export` | [`src/html2md/log_export.py:main`](src/html2md/log_export.py) | JSONL-to-CSV log export utility |
| `python -m html2md` | [`src/html2md/__main__.py`](src/html2md/__main__.py) | Module execution, delegates to `cli.main()` |

## Key Files

| File | Description |
|---|---|
| `src/html2md/cli.py` | Main CLI module |
| `src/html2md/log_export.py` | Reads JSONL logs and exports selected fields to CSV |
| `src/html2md/__init__.py` | Package init, exposes `__version__` |
| `tests/test_cli_smoke.py` | Smoke test verifying `--help` exits cleanly |
| `setup-html2md.ps1` | Windows PowerShell setup (venv, deps, PATH) |
| `gui-url-convert.ps1` | Windows WPF GUI for URL conversion |
| `run-html2md.bat` | Windows batch launcher |
| `run-gui.bat` | Windows GUI launcher |

## Features

- HTML to Markdown/PDF/TXT conversion with `--url` support
- Multi-format export
- ReportLab PDF rendering
- Per-domain rate limiting policies
- Robots.txt and meta tag controls
- Retries with backoff
- JSONL-based logging with CSV export
- Title-fetch deduplication
- Validation tool
- Windows bootstrap and GUI prompt support
