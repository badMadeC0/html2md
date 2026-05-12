#!/usr/bin/env python3
"""PreToolUse hook: block Edit/Write to sensitive files.

Reads a Claude Code hook payload on stdin (JSON) and exits non-zero with a
diagnostic on stderr when the targeted path matches a sensitive pattern.
Stdlib only.

Sensitive patterns (matched against the file's basename and against the
full path) — see `SENSITIVE_BASENAME_PATTERNS` below for the canonical
list. Covers every pattern in pr-rules/common.md §3 (`.env*`, `*.pem`,
`*.key`, `*.crt`, `credentials.json`, `id_{rsa,ed25519,ecdsa,dsa}*`) plus
the broader secret-naming conventions called out by §3's "any file
matching a sensible secret naming convention" clause: bare `secrets`/
`secret`/`credentials`, `secrets.*`/`secret.*`/`credentials.*`,
`*.secret(s)(.*)`, `*api[-_]token*`, and `*[-_]credentials(.*)`. Files
inside a `secrets/`, `secret/`, or `credentials/` directory are also
treated as sensitive via `SENSITIVE_DIR_SEGMENTS`.
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
    # SSH private keys: cover all standard key types, not just RSA.
    "id_rsa*",
    "id_ed25519*",
    "id_ecdsa*",
    "id_dsa*",
    # "any file matching a sensible secret naming convention" (per
    # pr-rules/common.md §3). Use broad globs rather than enumerating
    # each extension — `credentials.toml`, `secrets.env`, etc. are equally
    # sensitive and easy to miss. Err on the side of false-positive block
    # for unfamiliar names rather than false-negative leak.
    #
    # Both extensionless basenames (`secrets`, `secret`, `credentials`,
    # `prod-credentials`) and any-extension forms are covered.
    "secrets",
    "secret",
    "credentials",
    "secrets.*",
    "secret.*",
    "credentials.*",
    "*.secret",
    "*.secret.*",
    "*.secrets",
    "*.secrets.*",
    "*api-token*",
    "*api_token*",
    "*-credentials",
    "*_credentials",
    "*-credentials.*",
    "*_credentials.*",
)
PATH_KEYS = {"file_path", "path", "notebook_path"}

# Directory names whose contents are uniformly sensitive. Any path whose
# segments include one of these (e.g. `secrets/prod.json`,
# `config/credentials/token.yaml`) is treated as sensitive regardless of
# the leaf basename. Matched against lower-cased path segments.
SENSITIVE_DIR_SEGMENTS = frozenset({
    "secrets",
    "secret",
    "credentials",
})


def is_sensitive(path: str) -> bool:
    if not path:
        return False
    normalized_path = path.replace("\\", "/").lower()
    segments = normalized_path.split("/")
    normalized_base = segments[-1]
    # Any path component that names a sensitive directory taints
    # everything below it. The basename-only check would otherwise miss
    # files like `secrets/prod.json` whose leaf is just `prod.json`.
    if any(seg in SENSITIVE_DIR_SEGMENTS for seg in segments[:-1]):
        return True
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

    if not isinstance(payload, dict):
        print("protect-sensitive-files: BLOCKED — hook payload must be a JSON object",
              file=sys.stderr)
        return 2

    tool_name = payload.get("tool_name") or ""
    if tool_name not in {"Edit", "Write", "MultiEdit", "NotebookEdit"}:
        return 0  # not our concern

    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, (dict, list)):
        print(
            f"protect-sensitive-files: BLOCKED — unsupported {tool_name} tool_input shape",
            file=sys.stderr,
        )
        return 2

    candidates = _collect_candidate_paths(tool_input)

    # Fail-closed when an in-scope tool has no recognized path keys: a
    # future Claude Code version that uses different keys (e.g. `target`,
    # `file`) would otherwise bypass this hook silently. Block and surface
    # the unknown shape so a human can update PATH_KEYS rather than learn
    # about the bypass after the fact.
    if not candidates:
        try:
            shape = sorted(tool_input.keys()) if isinstance(tool_input, dict) else type(tool_input).__name__
        except Exception:
            shape = "<unknown>"
        print(
            f"protect-sensitive-files: BLOCKED — {tool_name} payload has no "
            f"recognized path keys (saw: {shape}). Update PATH_KEYS in "
            f".claude/hooks/protect-sensitive-files.py if this is a real tool.",
            file=sys.stderr,
        )
        return 2

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
