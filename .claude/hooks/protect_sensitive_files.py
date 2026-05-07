#!/usr/bin/env python3
"""Block Claude Code edits to files that commonly contain secrets.

The hook reads a Claude Code ``PreToolUse`` JSON payload from standard input and
returns a non-zero status when an Edit, Write, MultiEdit, or NotebookEdit tool is
targeting a sensitive file path.
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from typing import Any


BLOCKED_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
SENSITIVE_PATH_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.crt",
    "credentials.json",
    "id_rsa",
    "id_rsa.pub",
)
PATH_KEYS = ("file_path", "path", "notebook_path")


def _matches_sensitive_pattern(path: str) -> bool:
    """Return True when path or basename matches a sensitive-file pattern."""
    normalized_path = os.path.realpath(path).lower()
    normalized_base = os.path.basename(normalized_path)

    return any(
        fnmatch.fnmatchcase(normalized_base, pattern)
        or fnmatch.fnmatchcase(normalized_path, pattern)
        for pattern in SENSITIVE_PATH_PATTERNS
    )


def is_sensitive(path: str) -> bool:
    """Return True when ``path`` targets a sensitive file name."""
    if not path:
        return False
    return _matches_sensitive_pattern(path)


def _candidate_paths(tool_input: dict[str, Any]) -> list[str]:
    """Collect path-like fields from a Claude Code tool input payload."""
    return [
        value
        for key in PATH_KEYS
        if isinstance((value := tool_input.get(key)), str) and value
    ]


def main(argv: list[str] | None = None) -> int:
    """Validate a Claude Code hook payload from stdin.

    Args:
        argv: Unused command-line arguments, accepted for entry-point symmetry.

    Returns:
        ``2`` when a sensitive file edit should be blocked; otherwise ``0``.
    """
    del argv

    try:
        payload_raw = sys.stdin.read()
    except OSError as exc:  # pragma: no cover - defensive
        print(
            f"protect-sensitive-files: failed to read stdin: {exc}",
            file=sys.stderr,
        )
        return 0

    if not payload_raw.strip():
        return 0

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        print(f"protect-sensitive-files: bad JSON payload: {exc}", file=sys.stderr)
        return 0

    tool_name = payload.get("tool_name") or ""
    if tool_name not in BLOCKED_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}
    if not isinstance(tool_input, dict):
        return 0

    for path in _candidate_paths(tool_input):
        if is_sensitive(path):
            print(
                f"protect-sensitive-files: BLOCKED - refusing to {tool_name} "
                f"sensitive file: {path}",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
