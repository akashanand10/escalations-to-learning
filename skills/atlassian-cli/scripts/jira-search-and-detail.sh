#!/usr/bin/env bash
# jira-search-and-detail.sh — Run a JQL search, then fetch full details in parallel.
#
# Usage:
#   ./jira-search-and-detail.sh 'project = BP AND type = Bug'
#   # Outputs a JSON array of detailed ticket objects.
#
# Environment:
#   ACLI    — path to acli binary (default: acli in PATH)
#   JOBS    — parallelism level (default: 5)

set -euo pipefail

ACLI="${ACLI:-acli}"
JOBS="${JOBS:-5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ $# -lt 1 ]]; then
  echo "Usage: jira-search-and-detail.sh '<JQL query>'" >&2
  exit 1
fi

JQL="$1"

echo "Searching: $JQL" >&2

# Step 1: Search and extract keys
KEYS=$("$ACLI" jira workitem search --jql "$JQL" --paginate --json \
  | jq -r '.[].key')

COUNT=$(echo "$KEYS" | wc -l | tr -d ' ')
echo "Found $COUNT tickets. Fetching details (parallelism=$JOBS)..." >&2

# Step 2: Parallel detail fetch
echo "$KEYS" | "$SCRIPT_DIR/jira-bulk-details.sh"
