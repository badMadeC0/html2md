
# `html2md` Code Project

## Project Overview

`html2md` is a Python command-line utility designed to convert HTML content from a given URL into Markdown format. The project also includes secondary utilities for exporting JSONL log files to CSV format and for uploading files to the Anthropic API. A WPF-based GUI is also available for Windows users to perform conversions without using the command line.

The core technologies used are Python 3.8+, with `setuptools` for packaging. Key libraries include `requests` for fetching web content, `markdownify` and `beautifulsoup4` for the conversion process, `anthropic` for API interaction, and `reportlab` for potential PDF generation in the future. The project is structured with separate `src` and `tests` directories, and uses `pytest` for testing and GitHub Actions for continuous integration.

## Building and Running

### Setup

To set up the development environment, create a virtual environment and install the dependencies:

```bash
python -m venv .venv
.venv/Scripts/activate
pip install -e .
```

### Running the CLI

The main entry point for the CLI is `html2md`. You can run it directly or through the Python module:

- **Convert a single URL:**

    ```bash
    html2md --url "http://example.com" --outdir "output"
    ```

- **Convert a batch of URLs from a file:**

    ```bash
    html2md --batch "urls.txt" --outdir "output"
    ```

- **Run as a module:**

    ```bash
    python -m html2md --url "http://example.com"
    ```

### Running the Log Exporter

The log exporter can be run using the `html2md-log-export` command:

```bash
html2md-log-export --in "log.jsonl" --out "log.csv" --fields "ts,input,status"
```

### Running the Upload Utility

The upload utility can be run using the `html2md-upload` command:

```bash
html2md-upload "path/to/your/file"
```

### Running the GUI (Windows)

Windows users can use the PowerShell GUI:

```powershell
./gui-url-convert.ps1
```

Or the batch file launcher:

```batch
run-gui.bat
```

### Running Tests

Tests are run using `pytest`:

```bash
pytest
```

## Development Conventions

- The project follows a standard Python project structure with `src` and `tests` directories.
- It uses `pyproject.toml` for build configuration and dependency management, following modern Python packaging standards (PEP 517/518).
- The code includes type hints and is checked with `mypy`.
- The CLI tools include help messages and command-line argument parsing using Python's `argparse` module.
- The project includes helper scripts for Windows users, demonstrating a focus on cross-platform usability.

## Documentation Files

- README.md
- GEMINI.md
- CLAUDE.md
- .jules/palette.md
- .jules/sentinel.md
- docs/ml/00-overview.md
- .github/copilot-instructions.md

## License

MIT License

## Project Structure

```Txt
./
    MANIFEST.in
    run-html2md.bat
    README.md
    run-gui.bat
    pyproject.toml
    GEMINI.md
    .gitignore
    CLAUDE.md
    gui-url-convert.ps1
    setup-html2md.ps1
    tests/
        test_app.py
        test_csv_security.py
        test_log_export.py
        test_cli_smoke.py
        test_cli_error.py
        test_cli_exceptions.py
    .jules/
        palette.md
        sentinel.md
    docs/
        ml/
            00-overview.md
    .github/
        CODEOWNERS
        copilot-instructions.md
        dependabot.yml
        workflows/
            update-docs.yml
            copilot-setup-steps.yml
            ci.yml
            claude-agent.yml
            request-jules-review.yml
        scripts/
            generate_docs.py
            run_claude_agent.sh
    html2md/
        .mypy.ini
        pyproject.toml
        tests/
            __init__.py
            test_cli.py
    src/
        html2md_cli.egg-info/
            dependency_links.txt
            requires.txt
            SOURCES.txt
            top_level.txt
            PKG-INFO
            entry_points.txt
        html2md/
            __init__.py
            upload.py
            cli.py
            app.py
            log_export.py
            __main__.py

```

## Key Files

### `README.md`

```markdown

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

```

### `pyproject.toml`

```toml

[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "html2md-cli"
version = "0.11.6"
description = "Full HTML→Markdown/PDF/TXT converter with --url, multi-format export, ReportLab PDF rendering, Markdown conversion, per-domain rate policy, robots/meta controls, retries/backoff, JSONL logs + CSV export, title-fetch dedupe, validation tool, Windows bootstrap & GUI prompt."
readme = "README.md"
requires-python = ">=3.8"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "you@example.com" }]
keywords = ["html", "markdown", "pdf", "txt", "cli", "windows", "bootstrap", "rate limit", "regex", "logging", "reportlab", "markdownify"]
classifiers = [
  "Programming Language :: Python :: 3",
  "License :: OSI Approved :: MIT License",
  "Environment :: Console",
  "Topic :: Text Processing :: Markup",
]

dependencies = [
  "markdownify>=0.11.6",
  "beautifulsoup4>=4.10.0",
  "requests>=2.25.0",
  "reportlab>=3.6.0",
  "pillow>=9.0.0",
  "pyyaml>=6.0",
  "anthropic>=0.39.0",
]

[project.optional-dependencies]
deploy = [
  "flask>=2.0.0",
  "gunicorn>=20.1.0",
]

[project.scripts]
html2md = "html2md.cli:main"
html2md-log-export = "html2md.log_export:main"
html2md-upload = "html2md.upload:main"

[tool.setuptools]
package-dir = {"" = "src"}

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
addopts = "-q"

```

### `src/html2md/cli.py`

```python
"""CLI entry point for html2md."""

from __future__ import annotations
import argparse
import os
import sys

def main(argv=None):
    """Run the CLI."""
    ap = argparse.ArgumentParser(
        prog='html2md',
        description='Convert HTML URL to Markdown.'
    )
    ap.add_argument('--help-only', action='store_true', help=argparse.SUPPRESS)
    ap.add_argument('--url', help='Input URL to convert')
    ap.add_argument('--batch', help='File containing URLs to process (one per line)')
    ap.add_argument('--outdir', help='Output directory to save the file')

    args = ap.parse_args(argv)

    if args.help_only:
        ap.print_help()
        return 0

    if args.url or args.batch:
        try:
            import requests  # type: ignore  # pylint: disable=import-outside-toplevel
            from markdownify import markdownify as md  # pylint: disable=import-outside-toplevel
        except ImportError as e:
            print(f"Error: Missing dependency {e.name}."
                  "Please run: pip install requests markdownify", file=sys.stderr)
            return 1

        session = requests.Session()
        session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': (
                'text/html,application/xhtml+xml,application/xml;q=0.9,'
                'image/avif,image/webp,image/apng,*/*;q=0.8'
            ),
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
        })

        def process_url(target_url: str) -> None:
            """Process a single URL."""
            # Fix common URL typo: trailing slash before query parameters
            if '/?' in target_url:
                target_url = target_url.replace('/?', '?')

            print(f"Processing URL: {target_url}")

            try:
                print("Fetching content...")
                response = session.get(target_url, timeout=30)
                response.raise_for_status()

                print("Converting to Markdown...")
                md_content = md(response.text, heading_style="ATX")

                if args.outdir:
                    if not os.path.exists(args.outdir):
                        os.makedirs(args.outdir)

                    # Create a simple filename based on the URL
                    filename = "conversion_result.md"
                    url_path = target_url.split('?')[0].rstrip('/')
                    if url_path:
                        base = os.path.basename(url_path)
                        if base:
                            filename = f"{base}.md"

                    out_path = os.path.join(args.outdir, filename)
                    with open(out_path, 'w', encoding='utf-8') as f:
                        f.write(md_content)
                    print(f"Success! Saved to: {out_path}")
                else:
                    print(md_content)

            except requests.RequestException as e:
                print(f"Network error: {e}", file=sys.stderr)
            except OSError as e:
                print(f"File error: {e}", file=sys.stderr)
            except Exception as e:  # pylint: disable=broad-exception-caught
                print(f"Conversion failed: {e}", file=sys.stderr)

        if args.url:
            process_url(args.url)

        if args.batch:
            if not os.path.exists(args.batch):
                print(f"Error: Batch file not found: {args.batch}", file=sys.stderr)
                return 1
            with open(args.batch, 'r', encoding='utf-8') as f:
                for line in f:
                    u = line.strip()
                    if u:
                        process_url(u)

        return 0

    ap.print_help()
    return 0

```

### `src/html2md/log_export.py`

```python
"""Export html2md JSONL logs to CSV."""

import argparse
import csv
import json
from pathlib import Path

_DANGEROUS_PREFIXES = ("=", "+", "-", "@")


def _sanitize_formula(value: str) -> str:
    """Prefix strings that look like formulas to prevent CSV injection."""
    if value.startswith("'"):
        return value
    if value.lstrip().startswith(_DANGEROUS_PREFIXES):
        return f"'{value}"
    return value


def _unique_fieldnames(fields: list[str]) -> tuple[list[str], list[tuple[str, str]]]:
    """Return deduplicated/sanitized CSV headers and original->output mapping."""
    used: set[str] = set()
    out_fields: list[str] = []
    mapping: list[tuple[str, str]] = []

    for field in fields:
        base = _sanitize_formula(field)
        candidate = base
        suffix = 1
        while candidate in used:
            candidate = f"{base}_{suffix}"
            suffix += 1

        used.add(candidate)
        out_fields.append(candidate)
        mapping.append((field, candidate))

    return out_fields, mapping


def _sanitize_value(value: object) -> object:
    """Return CSV-safe value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return _sanitize_formula(value)
    return value


def main(argv=None):
    """Run the log export CLI."""
    ap = argparse.ArgumentParser(
        prog='html2md-log-export', description='Export html2md JSONL logs to CSV'
    )
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--out', dest='out', required=True)
    ap.add_argument('--fields', default='ts,input,output,status,reason')
    args = ap.parse_args(argv)

    fields = [f.strip() for f in args.fields.split(',') if f.strip()]
    fieldnames, mapping = _unique_fieldnames(fields)

    inp = Path(args.inp)
    out = Path(args.out)
    with inp.open('r', encoding='utf-8') as fi, out.open('w', newline='', encoding='utf-8') as fo:
        # Optimization: Use csv.writer instead of DictWriter to avoid per-row dictionary overhead
        w = csv.writer(fo)
        w.writerow(fieldnames)

        for line in fi:
            line = line.strip()
            if not line:
                continue

            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            if not isinstance(rec, dict):
                continue

            row = [
                _sanitize_value(rec.get(input_name, ""))
                for input_name, _ in mapping
            ]
            w.writerow(row)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

```

### `src/html2md/upload.py`

```python
"""Upload utility for html2md."""
from __future__ import annotations

import argparse
import mimetypes
import sys
from pathlib import Path
from typing import Any

import anthropic


def upload_file(file_path: str) -> Any:
    """Upload a file to the Anthropic API."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    mime_type, _ = mimetypes.guess_type(str(path))
    if mime_type is None:
        mime_type = "application/octet-stream"

    client = anthropic.Anthropic()
    with path.open("rb") as file_data:
        result = client.beta.files.upload(
            file=(path.name, file_data, mime_type),
        )
    return result


def main(argv=None):
    """Run the upload CLI."""
    ap = argparse.ArgumentParser(
        prog="html2md-upload",
        description="Upload a file to the Anthropic API.",
    )
    ap.add_argument("file", help="Path to the file to upload")
    args = ap.parse_args(argv)

    try:
        result = upload_file(args.file)
        print(f"File uploaded successfully. ID: {result.id}")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except anthropic.APIError as exc:
        print(f"API error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
