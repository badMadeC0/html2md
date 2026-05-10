#!/bin/sh
# Launch the sensitive-file protection hook without requiring Node or a
# pyenv-sensitive bare `python` shim. Prefer python3 on Unix-like systems, then
# the Windows `py -3` launcher when available, and use bare python only as a
# final fallback. If no launcher can evaluate the policy, fail closed with exit
# code 2 so Claude Code PreToolUse blocks the edit.

set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
HOOK_SCRIPT=$SCRIPT_DIR/protect_sensitive_files.py
PAYLOAD=$(mktemp "${TMPDIR:-/tmp}/protect-sensitive-files.XXXXXX") || exit 2
cleanup() {
    rm -f "$PAYLOAD"
}
trap cleanup EXIT HUP INT TERM

if ! cat > "$PAYLOAD"; then
    echo "protect-sensitive-files: failed to read stdin" >&2
    exit 2
fi

try_launcher() {
    command_name=$1
    shift

    if ! command -v "$command_name" >/dev/null 2>&1; then
        return 127
    fi

    "$@" "$HOOK_SCRIPT" < "$PAYLOAD"
    status=$?
    case $status in
        0|2)
            exit "$status"
            ;;
        126|127)
            echo "protect-sensitive-files: $command_name could not run; trying next Python launcher" >&2
            return "$status"
            ;;
        *)
            echo "protect-sensitive-files: $command_name exited with status $status; trying next Python launcher" >&2
            return "$status"
            ;;
    esac
}

try_launcher python3 python3
try_launcher py py -3
try_launcher python python

echo "protect-sensitive-files: no working Python 3 launcher found (tried python3, py -3, python)" >&2
exit 2
