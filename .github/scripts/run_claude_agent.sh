#!/usr/bin/env bash
set -uo pipefail

# Avoid failing the workflow for non-critical memory API 404s.
export DISABLE_MEMORY="${DISABLE_MEMORY:-true}"
export SKIP_MEMORY_FETCH="${SKIP_MEMORY_FETCH:-true}"

if [[ -z "${CLAUDE_COMMAND:-}" ]]; then
  echo "::error::CLAUDE_COMMAND is not set. Configure it as a repository variable in Settings > Secrets and variables > Actions > Variables."
  exit 1
fi

if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
  echo "::warning::ANTHROPIC_API_KEY secret is not set. Claude may fail to authenticate. Add it in Settings > Secrets and variables > Actions > Secrets."
fi

echo "Running Claude agent command..."
IFS=' ' read -r -a claude_cmd_array <<< "$CLAUDE_COMMAND"
"${claude_cmd_array[0]}" "${claude_cmd_array[@]:1}"
status=$?

if [[ $status -ne 0 ]]; then
  echo "::error::Claude agent exited with status ${status}."
  exit $status
fi

echo "Claude agent completed successfully."
