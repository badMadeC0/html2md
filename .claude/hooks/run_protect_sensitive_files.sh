#!/bin/sh
# Run the sensitive-file protection hook without requiring Node.
#
# Claude Code only blocks PreToolUse hooks when the command exits with status 2.
# This launcher preserves stdin for fallback Python launchers and fails closed with
# status 2 whenever the policy cannot be evaluated.

HOOK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 2
HOOK_SCRIPT=$HOOK_DIR/protect_sensitive_files.py
PAYLOAD_FILE=$(mktemp "${TMPDIR:-/tmp}/protect-sensitive-files.XXXXXX") || exit 2

cleanup() {
    rm -f "$PAYLOAD_FILE"
}
trap cleanup EXIT HUP INT TERM

if ! cat > "$PAYLOAD_FILE"; then
    echo "protect-sensitive-files: failed to read stdin; failing closed" >&2
    exit 2
fi

run_launcher() {
    "$@" "$HOOK_SCRIPT" < "$PAYLOAD_FILE"
    status=$?

    case "$status" in
        0|2)
            exit "$status"
            ;;
        126|127)
            return 1
            ;;
        *)
            echo "protect-sensitive-files: hook failed with status $status; failing closed" >&2
            exit 2
            ;;
    esac
}

run_launcher python3
run_launcher py -3
run_launcher python

echo "protect-sensitive-files: no working Python 3 launcher found; failing closed" >&2
exit 2
