#!/usr/bin/env bash
set -uo pipefail

# Avoid failing the workflow for non-critical memory API 404s.
export DISABLE_MEMORY="${DISABLE_MEMORY:-true}"
export SKIP_MEMORY_FETCH="${SKIP_MEMORY_FETCH:-true}"

if [[ -z "${CLAUDE_COMMAND:-}" ]]; then
  echo "CLAUDE_COMMAND is not set; skipping Claude agent run."
  exit 0
fi

echo "Running Claude agent command with memory fetch disabled..."
set +e
bash -lc "$CLAUDE_COMMAND"
status=$?
set -e

if [[ $status -ne 0 ]]; then
  echo "Claude agent exited with status ${status}. Continuing because this step is non-critical."
  exit 0
fi

echo "Claude agent completed successfully."
