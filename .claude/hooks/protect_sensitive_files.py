#!/usr/bin/env python3
"""Block Claude write tools from modifying local secret-bearing files.

The hook reads Claude Code's JSON payload from stdin and exits with status 2
when a requested edit targets files that commonly contain credentials. Missing
or unrecognized payload fields are allowed so the hook does not break unrelated
tool usage.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import PurePosixPath
from typing import Any, Iterable

BLOCKED_EXACT_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
    "credentials.json",
    "credentials.yml",
    "credentials.yaml",
    "secrets.json",
    "secrets.yml",
    "secrets.yaml",
}

BLOCKED_SUFFIXES = {
    ".key",
    ".pem",
    ".p12",
    ".pfx",
    ".crt",
    ".cer",
}

BLOCKED_SSH_KEY_PREFIXES = (
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
)

BLOCKED_PATH_PARTS = {
    ".aws",
    ".azure",
    ".gnupg",
    ".ssh",
}

PATH_FIELD_NAMES = {
    "file_path",
    "notebook_path",
    "path",
}


def main() -> int:
    """Evaluate the hook payload and return a Claude-compatible exit code.

    Returns:
        ``0`` when the requested tool use is allowed, or ``2`` when Claude
        should block it and display the stderr message.
    """
    payload = read_payload(sys.stdin.read())
    target_paths = list(extract_paths(payload.get("tool_input", payload)))
    blocked_paths = [path for path in target_paths if is_sensitive_path(path)]

    if not blocked_paths:
        return 0

    blocked_list = ", ".join(blocked_paths)
    print(
        f"Blocked edit to sensitive file path(s): {blocked_list}. "
        "Move secrets to an approved vault or redact them before editing.",
        file=sys.stderr,
    )
    return 2


def read_payload(raw_payload: str) -> dict[str, Any]:
    """Parse a Claude hook JSON payload.

    Args:
        raw_payload: JSON string supplied to the hook on stdin.

    Returns:
        Parsed JSON object, or an empty mapping when stdin is empty or invalid.
    """
    if not raw_payload.strip():
        return {}

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        return {}

    return payload if isinstance(payload, dict) else {}


def extract_paths(value: Any) -> Iterable[str]:
    """Yield path-like values from Claude tool input payloads.

    Args:
        value: A nested JSON-compatible value from a hook payload.

    Yields:
        String values from known path fields such as ``file_path`` and
        ``notebook_path``.
    """
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PATH_FIELD_NAMES and isinstance(item, str):
                yield item
            else:
                yield from extract_paths(item)
    elif isinstance(value, list):
        for item in value:
            yield from extract_paths(item)


def is_sensitive_path(path: str) -> bool:
    """Return whether a path is likely to contain credentials.

    Args:
        path: Candidate filesystem path from a Claude write tool.

    Returns:
        ``True`` when the path matches common secret file names, suffixes, or
        credential directories; otherwise ``False``.
    """
    normalized_path = PurePosixPath(path.replace(os.sep, "/"))
    name = normalized_path.name.lower()
    parts = {part.lower() for part in normalized_path.parts}

    return (
        name in BLOCKED_EXACT_NAMES
        or name.startswith(".env.")
        or name.startswith(BLOCKED_SSH_KEY_PREFIXES)
        or normalized_path.suffix.lower() in BLOCKED_SUFFIXES
        or bool(parts & BLOCKED_PATH_PARTS)
    )


if __name__ == "__main__":
    raise SystemExit(main())
