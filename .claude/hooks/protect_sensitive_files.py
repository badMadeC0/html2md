#!/usr/bin/env python3
"""Block Claude Code edits to sensitive files.

This PreToolUse hook reads a Claude Code hook payload from standard input and
exits with a non-zero status when an Edit, Write, MultiEdit, or NotebookEdit
request targets a sensitive path.
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys
from typing import Any, Dict, List, Optional


SENSITIVE_BASENAME_PATTERNS = (
    ".env*",
    "*.pem",
    "*.key",
    "*.crt",
    "credentials.json",
    "id_rsa*",
    "id_ed25519*",
)
PROTECTED_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
PATH_KEYS = ("file_path", "path", "notebook_path")


def is_sensitive(path: str) -> bool:
    """Return whether a path matches a sensitive filename pattern.

    Args:
        path: File path from a Claude Code tool input payload.

    Returns:
        True when the basename or normalized path matches a sensitive pattern;
        otherwise False.
    """
    if not path:
        return False

    normalized_path = path.replace("\\", "/").lower()
    normalized_base = os.path.basename(normalized_path).lower()

    for pattern in SENSITIVE_BASENAME_PATTERNS:
        normalized_pattern = pattern.lower()
        if fnmatch.fnmatchcase(normalized_base, normalized_pattern):
            return True
        if fnmatch.fnmatchcase(normalized_path, f"*/{normalized_pattern}"):
            return True
        if fnmatch.fnmatchcase(normalized_path, normalized_pattern):
            return True

    return False


def _load_payload() -> Optional[Dict[str, Any]]:
    """Read and parse a hook payload from standard input.

    Returns:
        A parsed JSON object, or None when input is empty or malformed.

    Side Effects:
        Writes diagnostics to standard error for malformed input or read errors.
    """
    try:
        payload_raw = sys.stdin.read()
    except Exception as exc:  # pragma: no cover - defensive fallback
        print(f"protect-sensitive-files: failed to read stdin: {exc}", file=sys.stderr)
        return None

    if not payload_raw.strip():
        return None

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        print(f"protect-sensitive-files: bad JSON payload: {exc}", file=sys.stderr)
        return None

    if not isinstance(payload, dict):
        return None

    return payload


def _target_paths(tool_input: Any) -> List[str]:
    """Extract candidate target paths from a Claude Code tool input.

    Args:
        tool_input: The ``tool_input`` value from the hook payload.

    Returns:
        A list of non-empty path strings to inspect.
    """
    candidates = []

    if isinstance(tool_input, dict):
        for key, value in tool_input.items():
            if key in PATH_KEYS and isinstance(value, str) and value:
                candidates.append(os.path.realpath(value))
            elif isinstance(value, (dict, list)):
                candidates.extend(_target_paths(value))
    elif isinstance(tool_input, list):
        for item in tool_input:
            candidates.extend(_target_paths(item))

    return candidates


def main(argv: Optional[List[str]] = None) -> int:
    """Run the PreToolUse sensitive-file guard.

    Args:
        argv: Unused command-line arguments; accepted for testability.

    Returns:
        Process exit status. ``2`` blocks a sensitive file edit; ``0`` allows
        the tool call or fails open for malformed hook input.
    """
    _ = argv
    payload = _load_payload()
    if payload is None:
        return 0

    tool_name = payload.get("tool_name") or ""
    if tool_name not in PROTECTED_TOOLS:
        return 0

    for path in _target_paths(payload.get("tool_input") or {}):
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
