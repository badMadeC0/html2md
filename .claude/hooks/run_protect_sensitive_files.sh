#!/bin/sh
# Launch the sensitive-file protection hook without relying on pyenv's
# repository-local `python` shim. Prefer python3, then the Windows py launcher,
# and only use bare python as a final fallback. If no launcher can evaluate the
# policy, fail closed so Claude Code PreToolUse blocks the attempted edit.

HOOK_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
HOOK_SCRIPT=$HOOK_DIR/protect_sensitive_files.py
PAYLOAD_FILE=$(mktemp "${TMPDIR:-/tmp}/protect-sensitive-files.XXXXXX") || {
  echo "protect-sensitive-files: failed to create temporary payload file" >&2
  exit 2
}
trap 'rm -f "$PAYLOAD_FILE"' EXIT HUP INT TERM

cat > "$PAYLOAD_FILE" || {
  echo "protect-sensitive-files: failed to read stdin" >&2
  exit 2
}

run_candidate() {
  command_name=$1
  shift

  if ! command -v "$command_name" >/dev/null 2>&1; then
    return 127
  fi

  "$command_name" "$@" "$HOOK_SCRIPT" < "$PAYLOAD_FILE"
}

for candidate in python3 "py -3" python; do
  # shellcheck disable=SC2086 # candidate intentionally expands py into py -3.
  run_candidate $candidate
  status=$?

  case $status in
    0|2)
      exit "$status"
      ;;
    126|127)
      ;;
    *)
      echo "protect-sensitive-files: $candidate exited with status $status; trying next Python launcher" >&2
      ;;
  esac
done

echo "protect-sensitive-files: no working Python 3 launcher found (tried python3, py -3, python)" >&2
exit 2
