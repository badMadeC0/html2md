# `html2md` Code Project

## Project Overview

`html2md` is a Python command-line utility designed to convert HTML content from a given URL into Markdown format. The project also includes secondary utilities for exporting JSONL log files to CSV format and for uploading files to the Anthropic API. A WPF-based GUI is also available for Windows users to perform conversions without using the command line.

The core technologies used are Python 3.8+, with `setuptools` for packaging. Key libraries include `requests` for fetching web content, `markdownify` and `beautifulsoup4` for the conversion process, `anthropic` for API interaction, and `reportlab` for potential PDF generation in the future. The project is structured with separate `src` and `tests` directories, and uses `pytest` for testing and GitHub Actions for continuous integration.

## Building and Running

### Setup

To set up the development environment, create a virtual environment and install the dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```

### Running the CLI

The main entry point for the CLI is `html2md`. You can run it directly or through the Python module:

-   **Convert a single URL:**

    ```bash
    html2md --url "http://example.com" --outdir "output"
    ```

-   **Convert a batch of URLs from a file:**

    ```bash
    html2md --batch "urls.txt" --outdir "output"
    ```

-   **Run as a module:**

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

-   The project follows a standard Python project structure with `src` and `tests` directories.
-   It uses `pyproject.toml` for build configuration and dependency management, following modern Python packaging standards (PEP 517/518).
-   The code includes type hints and is checked with `mypy`.
-   The CLI tools include help messages and command-line argument parsing using Python's `argparse` module.
-   The project includes helper scripts for Windows users, demonstrating a focus on cross-platform usability.
