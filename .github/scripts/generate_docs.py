import os

def get_project_structure():
    """Gets the project structure."""
    structure = ""
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if ".mypy_cache" in dirs:
            dirs.remove(".mypy_cache")
        if ".pytest_cache" in dirs:
            dirs.remove(".pytest_cache")

        level = root.replace(".", "").count(os.sep)
        indent = " " * 4 * (level)
        structure += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = " " * 4 * (level + 1)
        for f in files:
            structure += f"{sub_indent}{f}\n"
    return structure

def get_file_content(filepath):
    """Gets the content of a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def get_markdown_files():
    """Gets all markdown files in the repository."""
    markdown_files = []
    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if ".mypy_cache" in dirs:
            dirs.remove(".mypy_cache")
        if ".pytest_cache" in dirs:
            dirs.remove(".pytest_cache")

        for f in files:
            if f.endswith(".md"):
                markdown_files.append(os.path.join(root, f))
    return markdown_files

def generate_gemini_md():
    """Generates the GEMINI.md file."""
    project_structure = get_project_structure()
    readme_content = get_file_content("README.md")
    pyproject_content = get_file_content("pyproject.toml")
    cli_content = get_file_content("src/html2md/cli.py")
    log_export_content = get_file_content("src/html2md/log_export.py")
    upload_content = get_file_content("src/html2md/upload.py")
    markdown_files = get_markdown_files()
    markdown_files_str = "\n".join(f"- {f}" for f in markdown_files)

    gemini_md_content = f"""
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

## Documentation Files

{markdown_files_str}

## License

MIT License
## Project Structure

```
{project_structure}
```

## Key Files

### `README.md`

```markdown
{readme_content}
```

### `pyproject.toml`

```toml
{pyproject_content}
```

### `src/html2md/cli.py`

```python
{cli_content}
```

### `src/html2md/log_export.py`

```python
{log_export_content}
```

### `src/html2md/upload.py`

```python
{upload_content}
```
"""

    with open("GEMINI.md", "w", encoding="utf-8") as f:
        f.write(gemini_md_content)

if __name__ == "__main__":
    generate_gemini_md()
