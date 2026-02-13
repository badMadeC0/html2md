# CLAUDE.md - Claude Code Review Configuration

## Project Overview
html2md is a Python project with a placeholder CLI and supporting tooling in this repository. The codebase currently includes a CLI stub (`src/html2md/cli.py`), a JSONL-to-CSV log export utility (`src/html2md/log_export.py`), and Windows launcher/setup scripts. The full production HTML-to-Markdown runtime is not included in this repository.

## Build & Test
```bash
pip install -e .
pip install pytest
pytest -q
```

## Project Structure
- `pyproject.toml` - Project metadata, dependencies, and build configuration
- `src/html2md/` - Main Python package
  - `cli.py` - CLI entry point (placeholder stub)
  - `log_export.py` - JSONL-to-CSV log export utility
- `tests/` - Test suite
- `gui-url-convert.ps1` - Windows WPF GUI script
- `setup-html2md.ps1` - Windows bootstrap/setup script
- `run-gui.bat` - Windows batch launcher for the GUI
- `run-html2md.bat` - Windows batch launcher for the CLI

## Code Review Guidelines
- Target runtime is Python 3.8+
- CI runs on `windows-latest` via GitHub Actions
- Tests use `pytest`
- Prefer feedback that matches code currently present in this repository
