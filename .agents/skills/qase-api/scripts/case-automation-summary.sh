#!/usr/bin/env bash
# Shows total, automated, manual, and to-be-automated test case counts for a project.
# Usage: ./case-automation-summary.sh <PROJECT_CODE>
#   e.g. ./case-automation-summary.sh ABP

set -euo pipefail

PROJECT="${1:?Usage: $0 <PROJECT_CODE>}"
source ~/.qase-credentials 2>/dev/null || true

TOTAL=$(curl -sg "https://api.qase.io/v1/case/${PROJECT}?limit=1" \
  -H "Token: $QASE_API_TOKEN" | jq '.result.total')

TMPFILE=$(mktemp /tmp/qase-cases-XXXXXX.json)
trap 'rm -f "$TMPFILE"' EXIT

python3 "$(dirname "$0")/qase-rest.py" list-cases --project "$PROJECT" --paginate > "$TMPFILE"

AUTOMATED=$(jq '[.[] | select(.isManual == false)] | length' "$TMPFILE")
MANUAL=$(jq '[.[] | select(.isManual == true)] | length' "$TMPFILE")
TO_BE_AUTOMATED=$(jq '[.[] | select(.isToBeAutomated == true)] | length' "$TMPFILE")

echo "Project:          $PROJECT"
echo "Total cases:      $TOTAL"
echo "Automated:        $AUTOMATED"
echo "Manual:           $MANUAL"
echo "To be automated:  $TO_BE_AUTOMATED"
