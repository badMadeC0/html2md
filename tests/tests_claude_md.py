"""Tests for CLAUDE.md documentation file."""
from __future__ import annotations

import re
from pathlib import Path


def get_claude_md_path() -> Path:
    """Return path to CLAUDE.md in the repository root."""
    return Path(__file__).parent.parent / "CLAUDE.md"


def read_claude_md() -> str:
    """Read CLAUDE.md content."""
    path = get_claude_md_path()
    return path.read_text(encoding="utf-8")


def test_claude_md_exists() -> None:
    """Verify CLAUDE.md file exists."""
    assert get_claude_md_path().exists(), "CLAUDE.md not found"


def test_required_sections_present() -> None:
    """Verify all required main sections are present."""
    content = read_claude_md()
    required_sections = [
        "# CLAUDE.md",
        "## Project Overview",
        "## Repository Structure",
        "## Key Entry Points",
        "## Development Setup",
        "## Build System",
        "## Testing",
        "## CI/CD",
        "## Code Conventions",
        "## Common Tasks",
        "## Architecture Notes",
    ]
    for section in required_sections:
        assert section in content, f"Missing section: {section}"


def test_all_fenced_code_blocks_have_language() -> None:
    """Verify all fenced code blocks specify a language (MD040)."""
    content = read_claude_md()
    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        if line.startswith("```"):
            # Extract language specifier
            match = re.match(r"^```([a-z0-9+\-.]*)", line)
            if match:
                lang = match.group(1)
                assert lang, (
                    f"Line {i}: Fenced code block missing language specification"
                )


def test_code_block_languages_valid() -> None:
    """Verify code block languages are recognized."""
    content = read_claude_md()
    valid_languages = {
        "bash",
        "python",
        "plaintext",
        "yaml",
        "json",
        "powershell",
        "batchfile",
    }
    pattern = r"^```([a-z0-9+\-.]+)"
    for match in re.finditer(pattern, content, re.MULTILINE):
        lang = match.group(1)
        assert lang in valid_languages, (
            f"Unrecognized language: {lang}"
        )


def test_key_entry_points_table_present() -> None:
    """Verify Key Entry Points table exists and is well-formed."""
    content = read_claude_md()
    assert "## Key Entry Points" in content, "Key Entry Points section missing"
    entry_section = content.split("## Key Entry Points")[1].split("##")[0]
    assert "| Command | Module | Description |" in entry_section, (
        "Key Entry Points table header missing"
    )
    assert "`html2md`" in entry_section, "html2md entry point missing"
    assert "`html2md-log-export`" in entry_section, "html2md-log-export entry point missing"


def test_repository_structure_paths_reasonable() -> None:
    """Verify paths in Repository Structure section are documented."""
    content = read_claude_md()
    repo_section = content.split("## Repository Structure")[1].split("##")[0]

    required_paths = [
        "src/html2md/",
        "tests/",
        ".github/",
        "pyproject.toml",
        "README.md",
    ]
    for path in required_paths:
        assert path in repo_section, f"Missing expected path: {path}"


def test_python_version_requirement() -> None:
    """Verify Python version requirement is documented."""
    content = read_claude_md()
    assert "Python >= 3.8" in content or "Python 3.8" in content, (
        "Python 3.8+ requirement not documented"
    )


def test_runtime_dependencies_listed() -> None:
    """Verify key runtime dependencies are documented."""
    content = read_claude_md()
    required_deps = [
        "markdownify",
        "beautifulsoup4",
        "requests",
        "reportlab",
        "pillow",
        "pyyaml",
    ]
    for dep in required_deps:
        assert dep in content, f"Missing dependency documentation: {dep}"


def test_ci_cd_section_complete() -> None:
    """Verify CI/CD section documents key details."""
    content = read_claude_md()
    ci_section = content.split("## CI/CD")[1].split("##")[0]
    required_info = [
        "windows-latest",
        "pytest",
        "pip install -e",
    ]
    for info in required_info:
        assert info in ci_section, f"CI/CD section missing: {info}"


def test_code_conventions_documented() -> None:
    """Verify code conventions are properly documented."""
    content = read_claude_md()
    conventions = content.split("## Code Conventions")[1].split("##")[0]
    required_conventions = [
        "from __future__ import annotations",
        "main(argv=None)",
        "argparse.ArgumentParser",
        "pathlib.Path",
        "UTF-8",
        "MIT",
    ]
    for convention in required_conventions:
        assert convention in conventions, f"Missing convention: {convention}"


def test_placeholder_stub_documented() -> None:
    """Verify cli.py placeholder stub nature is documented."""
    content = read_claude_md()
    architecture = content.split("## Architecture Notes")[1]
    assert "placeholder stub" in architecture.lower(), (
        "cli.py placeholder stub not documented in Architecture Notes"
    )
    assert "separate packaged build" in architecture, (
        "Separate packaged build note missing"
    )


def test_log_export_documented() -> None:
    """Verify log_export.py utility is documented."""
    content = read_claude_md()
    assert "log_export.py" in content, "log_export.py not documented"
    assert "html2md-log-export" in content, "html2md-log-export entry point not documented"
    assert "JSONL" in content, "JSONL log format not mentioned"
    assert "CSV" in content, "CSV export not mentioned"


def test_common_tasks_table_format() -> None:
    """Verify Common Tasks section has proper table format."""
    content = read_claude_md()
    assert "## Common Tasks" in content, "Common Tasks section missing"
    tasks_section = content.split("## Common Tasks")[1].split("##")[0]
    assert "| Task | Command |" in tasks_section, (
        "Common Tasks table header missing"
    )
    assert "|---|---|" in tasks_section, (
        "Common Tasks table separator missing"
    )
    assert "pytest -q" in tasks_section, "pytest command not in Common Tasks"


def test_build_system_documented() -> None:
    """Verify build system configuration is documented."""
    content = read_claude_md()
    build_section = content.split("## Build System")[1].split("##")[0]
    assert "pyproject.toml" in build_section, "pyproject.toml not mentioned in build system"
    assert "setuptools" in build_section, "setuptools not mentioned"
    assert "PEP 517" in build_section or "PEP 518" in build_section, (
        "PEP 517/518 standard not mentioned"
    )


def test_testing_framework_documented() -> None:
    """Verify testing framework and configuration are documented."""
    content = read_claude_md()
    testing_section = content.split("## Testing")[1].split("## CI/CD")[0]
    assert "pytest" in testing_section, "pytest not documented"
    assert "pytest -q" in testing_section, "pytest command not documented"
    assert "smoke test" in testing_section.lower(), "smoke tests not mentioned"
