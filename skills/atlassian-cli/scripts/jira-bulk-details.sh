#!/usr/bin/env bash
# jira-bulk-details.sh — Fetch detailed info for multiple Jira keys in parallel.
#
# Usage:
#   echo "KEY-1 KEY-2 KEY-3" | ./jira-bulk-details.sh
#   # or
#   ./jira-bulk-details.sh KEY-1 KEY-2 KEY-3
#
# Outputs a JSON array of extracted details (one per key).
# Requires: acli, jq, xargs
#
# Environment:
#   ACLI    — path to acli binary (default: acli in PATH)
#   JOBS    — parallelism level (default: 5)

set -euo pipefail

ACLI="${ACLI:-acli}"
JOBS="${JOBS:-5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DETAIL_JQ="$SCRIPT_DIR/jira-extract-detail.jq"

if [[ ! -f "$DETAIL_JQ" ]]; then
  echo "Error: jira-extract-detail.jq not found at $DETAIL_JQ" >&2
  exit 1
fi

# Collect keys from args or stdin (one key per line when piped)
if [[ $# -gt 0 ]]; then
  KEYS=("$@")
else
  KEYS=()
  while IFS= read -r line; do
    [[ -n "$line" ]] && KEYS+=("$line")
  done
fi

if [[ ${#KEYS[@]} -eq 0 ]]; then
  echo "Usage: jira-bulk-details.sh KEY-1 KEY-2 ..." >&2
  exit 1
fi

# Use an inline script string instead of export -f (which doesn't work in zsh)
printf '%s\n' "${KEYS[@]}" | xargs -P "$JOBS" -I {} bash -c '
  acli="$1"; jqf="$2"; key="$3"
  result=$("$acli" jira workitem view "$key" --fields "*all" --json 2>/dev/null) || {
    echo "{\"key\":\"$key\",\"error\":\"fetch failed\"}"
    exit 0
  }
  echo "$result" | jq -c -f "$jqf" 2>/dev/null || echo "{\"key\":\"$key\",\"error\":\"parse failed\"}"
' _ "$ACLI" "$DETAIL_JQ" {} | jq -s '.'
