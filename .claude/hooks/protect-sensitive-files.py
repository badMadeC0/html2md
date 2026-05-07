#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write to sensitive files.

Reads a Claude Code hook payload on stdin (JSON) and exits non-zero with a
diagnostic on stderr when the targeted path matches a sensitive pattern.
Stdlib only.

Sensitive patterns (matched against the file's basename and against the
full path) — covers the named patterns in pr-rules/common.md §3 plus
common secret-naming conventions (`secrets.*`, `*.secret(s).*`,
`*api[-_]token*`, `*-credentials.*`).
"""
from __future__ import annotations

import fnmatch
import json
import sys


SENSITIVE_BASENAME_PATTERNS = (
    # Documented in pr-rules/common.md §3.
    ".env*",
    "*.pem",
    "*.key",
    "*.crt",
    "credentials.json",
    "id_rsa*",
    # "any file matching a sensible secret naming convention" (per
    # pr-rules/common.md §3). Conservative set — additions welcome via
    # PR + edge-case ledger entry, but err on the side of false-positive
    # block for unfamiliar names rather than false-negative leak.
    "secrets.json",
    "secret.json",
    "secrets.yaml",
    "secrets.yml",
    "secret.yaml",
    "secret.yml",
    "*.secret",
    "*.secret.*",
    "*.secrets",
    "*.secrets.*",
    "*api-token*",
    "*api_token*",
    "*-credentials.*",
    "*_credentials.*",
)
PATH_KEYS = {"file_path", "path", "notebook_path"}


def is_sensitive(path: str) -> bool:
    if not path:
        return False
    normalized_path = path.replace("\\", "/").lower()
    normalized_base = normalized_path.rsplit("/", 1)[-1]
    for pat in SENSITIVE_BASENAME_PATTERNS:
        normalized_pat = pat.lower()
        if fnmatch.fnmatchcase(normalized_base, normalized_pat):
            return True
        if fnmatch.fnmatchcase(normalized_path, normalized_pat):
            return True
        if fnmatch.fnmatchcase(normalized_path, "*/" + normalized_pat):
            return True
    return False


def _collect_candidate_paths(value) -> list[str]:
    """Recursively collect file path strings from known path keys."""
    candidates = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in PATH_KEYS and isinstance(item, str) and item:
                candidates.append(item)
            candidates.extend(_collect_candidate_paths(item))
    elif isinstance(value, list):
        for item in value:
            candidates.extend(_collect_candidate_paths(item))
    return candidates


def main(argv=None) -> int:
    # Fail-closed: a sensitive-file guard that returns 0 (allow) on
    # malformed input would silently leak protection. If we cannot read or
    # parse the payload, block the tool call so the human investigates.
    try:
        payload_raw = sys.stdin.read()
    except Exception as exc:
        print(f"protect-sensitive-files: BLOCKED — failed to read stdin: {exc}",
              file=sys.stderr)
        return 2

    if not payload_raw.strip():
        print("protect-sensitive-files: BLOCKED — empty hook payload",
              file=sys.stderr)
        return 2

    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as exc:
        print(f"protect-sensitive-files: BLOCKED — bad JSON payload: {exc}",
              file=sys.stderr)
        return 2

    tool_name = payload.get("tool_name") or ""
    if tool_name not in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return 0  # not our concern

    tool_input = payload.get("tool_input") or {}
    candidates = _collect_candidate_paths(tool_input)

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
