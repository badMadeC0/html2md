#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write to sensitive files.

Reads a Claude Code hook payload on stdin (JSON) and exits non-zero with a
diagnostic on stderr when the targeted path matches a sensitive pattern.
Stdlib only.

Sensitive patterns (matched against the file's basename and against the
full path):
    .env, .env.<anything>, *.pem, *.key, *.crt,
    credentials.json, id_rsa, id_rsa.pub
"""
from __future__ import annotations

import fnmatch
import json
import os
import sys


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


def is_sensitive(path: str) -> bool:
    if not path:
        return False
    normalized_path = path.lower()
    normalized_base = os.path.basename(path).lower()
    for pat in SENSITIVE_BASENAME_PATTERNS:
        normalized_pat = pat.lower()
        if fnmatch.fnmatchcase(normalized_base, normalized_pat):
            return True
        # also match against the normalized full path so that e.g.
        # "config/.env" or "src/keys/id_rsa" still trigger
        if (
            fnmatch.fnmatchcase(normalized_path, "*/" + normalized_pat)
            or fnmatch.fnmatchcase(normalized_path, normalized_pat)
        ):
            return True
    return False


def main(argv=None) -> int:
    try:
        payload_raw = sys.stdin.read()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"protect-sensitive-files: failed to read stdin: {exc}",
              file=sys.stderr)
        return 0  # do not block on internal errors

    if not payload_raw.strip():
        return 0  # nothing to inspect, allow

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        print(f"protect-sensitive-files: bad JSON payload: {exc}",
              file=sys.stderr)
        return 0  # allow rather than break the agent on malformed input

    tool_name = payload.get("tool_name") or ""
    if tool_name not in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return 0  # not our concern

    tool_input = payload.get("tool_input") or {}
    candidates = []
    for key in ("file_path", "path", "notebook_path"):
        val = tool_input.get(key)
        if isinstance(val, str) and val:
            candidates.append(val)

    for path in candidates:
        if is_sensitive(path):
            print(
                f"protect-sensitive-files: BLOCKED — refusing to {tool_name} "
                f"sensitive file: {path}",
                file=sys.stderr,
            )
            return 2  # non-zero blocks the tool call

    return 0


if __name__ == "__main__":
    sys.exit(main())
