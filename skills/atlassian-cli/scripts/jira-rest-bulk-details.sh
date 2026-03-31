#!/usr/bin/env bash
# jira-rest-bulk-details.sh — Fetch full details for multiple Jira keys using the REST API.
#
# Usage:
#   echo "BP-1 BP-2 BP-3" | ./jira-rest-bulk-details.sh
#   # or
#   ./jira-rest-bulk-details.sh BP-1 BP-2 BP-3
#
# Outputs a JSON array of extracted details (one per key), in the same format
# as jira-bulk-details.sh. Requires: python3, jq.
#
# Credentials: see jira-rest.py for JIRA_SITE / JIRA_EMAIL / JIRA_TOKEN.

set -euo pipefail

JOBS="${JOBS:-5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DETAIL_JQ="$SCRIPT_DIR/jira-extract-detail.jq"
REST_CLIENT="$SCRIPT_DIR/jira-rest.py"

if [[ ! -f "$DETAIL_JQ" ]]; then
  echo "Error: jira-extract-detail.jq not found at $DETAIL_JQ" >&2
  exit 1
fi

if [[ ! -f "$REST_CLIENT" ]]; then
  echo "Error: jira-rest.py not found at $REST_CLIENT" >&2
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
  echo "Usage: jira-rest-bulk-details.sh BP-1 BP-2 ..." >&2
  exit 1
fi

printf '%s\n' "${KEYS[@]}" | xargs -P "$JOBS" -I {} bash -c '
  rest_client="$1"; jqf="$2"; key="$3"
  result=$(python3 "$rest_client" view "$key" 2>/dev/null) || {
    echo "{\"key\":\"$key\",\"error\":\"fetch failed\"}"
    exit 0
  }
  echo "$result" | jq -c -f "$jqf" 2>/dev/null || echo "{\"key\":\"$key\",\"error\":\"parse failed\"}"
' _ "$REST_CLIENT" "$DETAIL_JQ" {} | jq -s '.'
