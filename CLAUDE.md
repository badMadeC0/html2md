# CLAUDE.md

## Project Overview

**html2md-cli** (v0.11.6) is a Python CLI tool that converts HTML content to Markdown, PDF, and TXT formats. It supports URL fetching, per-domain rate limiting, robots.txt/meta tag controls, retries with backoff, JSONL logging, CSV export, and ReportLab PDF rendering. The project also includes Windows-specific setup scripts and a WPF GUI.

> **Note:** The CLI implementation in this repository is a placeholder stub. The full runtime is delivered via a separate packaged build.

## Repository Structure

```TEXT
html2md/
├── src/
│   └── html2md/
│       ├── __init__.py        # Package version
│       ├── __main__.py        # `python -m html2md` entry point
│       ├── cli.py             # Main CLI entry point (placeholder)
│       └── log_export.py      # JSONL-to-CSV log export utility
├── tests/
│   └── test_cli_smoke.py      # Smoke tests (pytest)
├── docs/
│   └── ml/
│       └── 00-overview.md     # ML documentation placeholder
├── .github/
│   └── workflows/
│       └── ci.yml             # GitHub Actions CI
├── pyproject.toml             # Project config, dependencies, build system
├── MANIFEST.in                # Source distribution includes
├── README.md                  # Project readme
├── run-html2md.bat            # Windows batch launcher
├── run-gui.bat                # Windows GUI launcher
├── setup-html2md.ps1          # Windows PowerShell setup script
└── gui-url-convert.ps1        # WPF GUI application (PowerShell)
```

## Key Entry Points

| Command | Module | Description |
| --------- | -------- | ------------- |
| `html2md` | `html2md.cli:main` | Main converter CLI |
| `html2md-log-export` | `html2md.log_export:main` | JSONL log to CSV exporter |
| `python -m html2md` | `html2md.__main__` | Module invocation |

## Development Setup

### Prerequisites

- Python >= 3.8

### Install (editable/dev mode)

```bash
pip install -e .
pip install pytest build
```

### Dependencies

**Runtime:**

- `markdownify>=0.11.6` — HTML to Markdown conversion
- `beautifulsoup4>=4.10.0` — HTML parsing
- `requests>=2.25.0` — HTTP fetching
- `idna>=2.5,<4` — IDNA hostname normalization for URL validation
- `reportlab>=3.6.0` — PDF generation
- `pillow>=9.0.0` — Image processing
- `pyyaml>=6.0` — YAML config parsing

**Dev:**

- `pytest` — Test framework
- `setuptools>=61`, `wheel` — Build tools

## Build System

Uses **PEP 517/518** with setuptools. Configuration is entirely in `pyproject.toml` (no `setup.py` or `setup.cfg`).

- Source layout: `src/` directory (`src/html2md/`)
- Build backend: `setuptools.build_meta`

## Testing

### Run tests

```bash
pytest -q
```

### Test details

- Framework: **pytest**
- Config: `pyproject.toml` → `[tool.pytest.ini_options]` with `addopts = "-q"`
- Tests live in `tests/`
- Current suite: smoke test verifying `html2md --help` command executes successfully

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):

- **Trigger:** push and pull_request
- **Runner:** `windows-latest`
- **Python:** `3.x` (latest stable)
- **Steps:**
  1. Upgrade pip, wheel, setuptools
  2. `pip install -e .` (install package in editable mode)
  3. `pip install pytest` (install test framework)
  4. `pytest -q` (run tests in quiet mode)

## Code Conventions

- **Language:** Python 3.8+ with `from __future__ import annotations`
- **Entry point pattern:** Functions named `main(argv=None)` accepting optional CLI args
- **CLI parsing:** `argparse.ArgumentParser`
- **Path handling:** `pathlib.Path`
- **Encoding:** UTF-8 throughout
- **Package version:** Single source of truth in `src/html2md/__init__.py` (`__version__`)
- **License:** MIT

## Common Tasks

| Task | Command |
| ------ | --------- |
| Install for development | `pip install -e .` then `pip install pytest build` |
| Run tests | `pytest -q` |
| Run the CLI | `html2md --help` |
| Export logs | `html2md-log-export --in logs.jsonl --out logs.csv` |
| Build package | `python -m build` |

## Architecture Notes

- The `cli.py` module is currently a **placeholder stub** that prints a message and exits. The full CLI with URL fetching, format conversion, rate limiting, and other features is delivered in a separate packaged build.
- `log_export.py` is a self-contained utility that reads JSONL log files and writes CSV output with configurable field selection (default fields: `ts,input,output,status,reason`).
- Windows integration scripts (`*.ps1`, `*.bat`) handle Python detection, venv creation, and GUI launching but are not part of the Python package itself.
