#!/usr/bin/env python3
"""PreToolUse hook that blocks edits to sensitive files.

Reads a Claude Code hook payload from stdin and exits non-zero with a diagnostic
on stderr when an Edit/Write-style tool targets a sensitive path. The hook is
stdlib-only so it can run in minimal environments.

Sensitive patterns are matched against both the basename and normalized path:
    .env, .env.<anything>, *.pem, *.key, *.crt,
    credentials.json, id_rsa, id_rsa.pub
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from typing import List, Optional, Sequence


SENSITIVE_BASENAME_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.crt",
    "credentials.json",
    "id_rsa",
    "id_rsa.pub",
)

PROTECTED_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
PATH_KEYS = ("file_path", "path", "notebook_path")


def is_sensitive(path: str) -> bool:
    """Return whether a path matches a sensitive-file pattern.

    Args:
        path: Candidate path from a tool input payload.

    Returns:
        True when the candidate basename or normalized path matches a protected
        pattern; otherwise False.
    """
    if not path:
        return False

    normalized_path = os.path.normpath(path)
    base = os.path.basename(normalized_path)
    for pattern in SENSITIVE_BASENAME_PATTERNS:
        if fnmatch.fnmatch(base, pattern):
            return True
        if fnmatch.fnmatch(normalized_path, "*/" + pattern) or fnmatch.fnmatch(
            normalized_path, pattern
        ):
            return True
    return False


def collect_candidate_paths(tool_input: object) -> List[str]:
    """Extract path candidates from a hook tool input.

    Args:
        tool_input: The ``tool_input`` value from a Claude Code hook payload.

    Returns:
        Non-empty string values for path-like keys used by Edit/Write tools.
    """
    if not isinstance(tool_input, dict):
        return []

    return [
        value
        for key in PATH_KEYS
        if isinstance((value := tool_input.get(key)), str) and value
    ]


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the hook.

    Args:
        argv: Unused command-line arguments, accepted for testability.

    Returns:
        ``2`` when a protected tool targets a sensitive path; otherwise ``0``.
    """
    del argv

    try:
        payload_raw = sys.stdin.read()
    except Exception as exc:  # pragma: no cover - defensive
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
        print(
            f"protect-sensitive-files: bad JSON payload: {exc}",
            file=sys.stderr,
        )
        return 0

    tool_name = payload.get("tool_name") or ""
    if tool_name not in PROTECTED_TOOLS:
        return 0

    for path in collect_candidate_paths(payload.get("tool_input")):
        if is_sensitive(path):
            print(
                f"protect-sensitive-files: BLOCKED — refusing to {tool_name} "
                f"sensitive file: {path}",
                file=sys.stderr,
            )
            return 2

    return 0


if __name__ == "__main__":
    sys.exit(main())
