#!/usr/bin/env python3
"""PreToolUse hook that blocks edits to sensitive files.

The hook reads a Claude Code hook payload from stdin and exits non-zero with a
stderr diagnostic when an Edit/Write-style tool targets a sensitive file path.
It is intentionally stdlib-only so it can run before project dependencies are
installed.
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from typing import Any, List, Optional


SENSITIVE_BASENAME_PATTERNS = (
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "*.crt",
    "credentials.json",
    "id_rsa",
    "id_rsa.pub",
    "id_ed25519",
    "id_ed25519.pub",
    "id_ecdsa",
    "id_ecdsa.pub",
    "id_dsa",
    "id_dsa.pub",
    "authorized_keys",
)

PROTECTED_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
PATH_KEYS = ("file_path", "path", "notebook_path")


def is_sensitive(path: str) -> bool:
    """Return whether ``path`` matches a sensitive filename pattern."""
    if not path:
        return False

    normalized_path = os.path.normpath(path)
    basename = os.path.basename(normalized_path)

    for pattern in SENSITIVE_BASENAME_PATTERNS:
        if fnmatch.fnmatch(basename, pattern):
            return True
        if fnmatch.fnmatch(normalized_path, pattern):
            return True
        if fnmatch.fnmatch(normalized_path, os.path.join("*", pattern)):
            return True

    return False


def candidate_paths(tool_input: Any) -> List[str]:
    """Extract and normalize target file paths recursively."""
    candidates = []
    if isinstance(tool_input, dict):
        for key, value in tool_input.items():
            if key in PATH_KEYS and isinstance(value, str) and value:
                candidates.append(os.path.realpath(value))
            elif isinstance(value, (dict, list)):
                candidates.extend(candidate_paths(value))
    elif isinstance(tool_input, list):
        for item in tool_input:
            candidates.extend(candidate_paths(item))
    return candidates


def main(argv: Optional[List[str]] = None) -> int:
    """Run the hook and return a process exit status."""
    del argv
    try:
        payload_raw = sys.stdin.read()
    except Exception as exc:  # pragma: no cover - defensive
        print(
            f"protect-sensitive-files: failed to read stdin: {exc}",
            file=sys.stderr,
        )
        return 2

    if not payload_raw.strip():
        print(
            "protect-sensitive-files: empty hook payload",
            file=sys.stderr,
        )
        return 2

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        print(
            f"protect-sensitive-files: bad JSON payload: {exc}",
            file=sys.stderr,
        )
        return 2

    if not isinstance(payload, dict):
        print(
            "protect-sensitive-files: hook payload must be a JSON object",
            file=sys.stderr,
        )
        return 2

    tool_name = payload.get("tool_name") or ""
    if tool_name not in PROTECTED_TOOLS:
        return 0

    tool_input = payload.get("tool_input") or {}

    for path in candidate_paths(tool_input):
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
