# Code Style Guide for Gemini Code Assist

## Project Context

html2md-cli is a Python CLI tool that converts HTML content to Markdown, PDF, and TXT formats.

## Language & Version

- Python 3.8+
- Use `from __future__ import annotations` in all modules

## Code Conventions

- Entry point functions should be named `main(argv=None)` accepting optional CLI args
- Use `argparse.ArgumentParser` for CLI parsing
- Use `pathlib.Path` for path handling
- Use UTF-8 encoding throughout
- Package version is sourced from `src/html2md/__init__.py` (`__version__`)

## Dependencies

- `markdownify` for HTML to Markdown conversion
- `beautifulsoup4` for HTML parsing
- `requests` for HTTP fetching
- `reportlab` for PDF generation
- `pillow` for image processing
- `pyyaml` for YAML config parsing

## Testing

- Use `pytest` as the test framework
- Tests live in the `tests/` directory
- Run tests with `pytest -q`

## Build System

- PEP 517/518 with setuptools
- Source layout uses `src/` directory
- All config in `pyproject.toml` (no setup.py or setup.cfg)

## Review Focus Areas

- Ensure backward compatibility with Python 3.8
- Check for proper error handling in CLI entry points
- Verify UTF-8 encoding is maintained
- Watch for security issues in URL fetching and file I/O
- Validate that new dependencies are added to pyproject.toml
