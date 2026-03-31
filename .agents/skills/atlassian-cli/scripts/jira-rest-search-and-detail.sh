#!/usr/bin/env bash
# jira-rest-search-and-detail.sh — End-to-end: JQL search → parallel detail fetch using REST API.
#
# Usage:
#   ./jira-rest-search-and-detail.sh 'project = BP AND type = "Engineering Escalation"'
#
# Outputs a JSON array of detailed ticket objects (same format as jira-search-and-detail.sh).
# Requires: python3, jq.
#
# Credentials: see jira-rest.py for JIRA_SITE / JIRA_EMAIL / JIRA_TOKEN.

set -euo pipefail

JOBS="${JOBS:-5}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REST_CLIENT="$SCRIPT_DIR/jira-rest.py"

if [[ $# -lt 1 ]]; then
  echo "Usage: jira-rest-search-and-detail.sh '<JQL query>'" >&2
  exit 1
fi

JQL="$1"

echo "Searching: $JQL" >&2

# Step 1: Search and extract keys
KEYS=$(python3 "$REST_CLIENT" search --jql "$JQL" --paginate | jq -r '.[].key')

COUNT=$(echo "$KEYS" | grep -c . || true)
echo "Found $COUNT tickets. Fetching details (parallelism=$JOBS)..." >&2

# Step 2: Parallel detail fetch
echo "$KEYS" | "$SCRIPT_DIR/jira-rest-bulk-details.sh"
