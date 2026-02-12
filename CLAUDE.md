# CLAUDE.md - Claude Code Review Configuration

## Project Overview
html2md is a Python CLI tool that converts HTML to Markdown, PDF, and TXT formats. It includes a Windows WPF GUI, rate limiting, robots/meta controls, retries with backoff, JSONL logging with CSV export, and a Windows bootstrap script.

## Build & Test
```bash
pip install -e .
pytest -q
```

## Project Structure
- `src/html2md/` - Main Python package
  - `cli.py` - CLI entry point
  - `log_export.py` - JSONL-to-CSV log export utility
- `tests/` - Test suite
- `gui-url-convert.ps1` - Windows WPF GUI
- `setup-html2md.ps1` - Windows bootstrap/setup script
- `run-gui.bat` / `run-html2md.bat` - Windows batch launchers

## Code Review Guidelines
- This project targets Python 3.8+
- CI runs on `windows-latest` via GitHub Actions
- Tests use pytest
