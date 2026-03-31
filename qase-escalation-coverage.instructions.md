---
description: "Use when: checking Qase test coverage for Jira escalation tickets, scoring existing test cases for relevancy, suggesting new test cases for gaps, and optionally creating them in Qase. Works for a single ticket or all tickets from an escalation analysis report."
---

# Qase Test Coverage for Jira Escalations

## Purpose

Map engineering escalation tickets (from Jira) to existing Qase test cases. Identify coverage gaps and, with user approval, suggest and create new test cases to prevent regressions.

## Input

Either:

- A **single Jira ticket key** (e.g. `BP-7789`) referenced from an escalation analysis file
- An **entire escalation analysis report** (e.g. `bp-engineering-escalations-february-2026-analysis.md`)

The escalation analysis file must follow the format from `jira-escalation-analysis.instructions.md` — each ticket has an Issue Summary, Product Area, Updates, and Next Action.

## Prerequisites

- Qase API access configured (see `skills/qase-api/SKILL.md` for setup)
- The relevant Qase project code (e.g. `ABP` for AP Automation / Bill Pay)
- The escalation analysis file must already exist with Issue Summaries populated

## Procedure

### Step 1: Extract ticket context

For each escalation ticket, collect:

1. **Ticket key** and title (e.g. `BP-7789 — Reports > All Bills Export Payment Completion Date Blank`)
2. **Issue Summary** — the 1-2 sentence root cause and resolution
3. **Product Area** — used to narrow the Qase search scope
4. **Key terms** — extract 3-5 searchable keywords from the summary (e.g. `payment completion date`, `bills export`, `partial payment`, `vendor-payment`)

### Step 2: Search Qase for existing coverage

Run progressively broader searches until results are found or coverage is confirmed absent:

```bash
REST=skills/qase-api/scripts/qase-rest.py

# 1. Search by most specific phrase
python3 $REST list-cases --project <CODE> --search "<specific phrase>" --paginate

# 2. Broaden to individual keywords
python3 $REST list-cases --project <CODE> --search "<keyword>" --paginate

# 3. List all cases and filter locally for partial matches
python3 $REST list-cases --project <CODE> --paginate | python3 -c "
import sys, json
data = json.load(sys.stdin)
keywords = ['keyword1', 'keyword2', 'keyword3']
for c in data:
    title_lower = c['title'].lower()
    if any(k in title_lower for k in keywords):
        print(f'  [{c[\"id\"]}] {c[\"title\"]}  (suite: {c.get(\"suite_id\", \"N/A\")})')
"

# 4. Check suites to find the right product area
python3 $REST list-suites --project <CODE> --paginate
```

### Step 3: Score relevancy

For each matching test case, assign a **relevancy score (0–100%)** based on:

| Score Range | Meaning                                                             |
| ----------- | ------------------------------------------------------------------- |
| 80–100%     | Directly tests the exact scenario or root cause from the escalation |
| 50–79%      | Tests the same feature area but not the specific failure mode       |
| 20–49%      | Tangentially related (same module, different functionality)         |
| 0–19%       | Only keyword overlap, functionally unrelated                        |

Present results in a table:

| Case ID | Title | Relevancy | Reason |
| ------- | ----- | --------- | ------ |

### Step 4: Report findings to user

**If relevant cases exist (any score >= 50%):**

- Present the scored table
- Highlight which specific scenarios from the escalation are covered vs. not
- Ask: "Would you like me to suggest additional test cases to close the remaining gaps?"

**If no relevant cases exist (all scores < 50% or no matches at all):**

- State clearly: "No direct test coverage exists for this issue in Qase."
- Ask: **"Would you like me to suggest test cases to cover this escalation?"**

> **IMPORTANT**: Do not suggest test cases without asking permission first.

### Step 5: Suggest test cases (upon approval)

When suggesting, follow these principles:

1. **Start with the exact bug scenario** — the case that would have caught this specific escalation
2. **Add the root cause edge case** — the specific technical condition from the RCA
3. **Add boundary cases** — happy path, empty state, in-progress state
4. **Keep to 3-6 cases** — enough to cover the issue without overengineering

For each suggestion, specify:

- Title (action-oriented, starts with "Verify")
- Type: Functional (type=1) or Regression (type=3)
- Priority: High (1) for bug-scenario cases, Medium (2) for boundary cases
- Severity: Critical (2) for exact-bug and RCA cases, Normal (4) for boundary cases
- Why it matters (one sentence)

Present as a table and ask: **"Would you like me to create any or all of these in Qase?"**

### Step 6: Create in Qase (upon approval)

Before creating:

1. **Check for existing suites** — search suites to see if an appropriate one exists
2. **Check for duplicate cases** — search for similar titles/coverage (per the duplicate-check rule in the Qase skill)
3. **Create suite hierarchy if needed** — create parent > child suites to match the product area (e.g. `AP Automation > Reports > All Bills Export`)
4. **Create cases** with full metadata (title, suite, priority, severity, type, description linking back to the Jira ticket)

Suite creation uses the Qase REST API directly:

```bash
curl -s -X POST "https://api.qase.io/v1/suite/<CODE>" \
  -H "Token: $QASE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "<Suite Name>", "parent_id": <parent_suite_id>}'
```

Case creation uses the Python client:

```bash
python3 $REST create-case --project <CODE> \
  --title "<title>" \
  --suite-id <id> \
  --priority <1|2|3> \
  --severity <1-6> \
  --type <1|3> \
  --description "<description linking to Jira ticket>"
```

### Step 7: Confirm and share links

After creation, list the created cases and provide Qase links:

```
https://app.qase.io/case/<CODE>-<case_id>
```

## Batch Mode (Full Analysis Report)

When processing an entire escalation analysis report:

1. Parse all tickets from the file (grep for `Issue:` lines)
2. For each ticket, run Steps 1–3
3. Present a **summary table** across all tickets:

| Jira Key | Title | Qase Coverage | Gaps |
| -------- | ----- | ------------- | ---- |

4. Ask: "Would you like me to suggest test cases for the tickets with no coverage?"
5. On approval, generate suggestions for all gap tickets and present together
6. On approval to create, batch-create all cases

## Lessons Learned

1. **Qase `--search` only matches exact substrings in titles** — it does not do fuzzy or semantic search. Always fall back to local keyword filtering against the full case list.
2. **Suite hierarchy matters** — create suites that match the Product Area taxonomy from the escalation analysis (e.g. Reports > All Bills Export, not just a flat "Reports" suite).
3. **Always link back to the Jira ticket** in the case description (e.g. "Regression test for BP-7789") so traceability is maintained.
4. **The `create-suite` command may not exist** in the Qase Python client — use `curl` against the REST API directly for suite creation.
5. **Severity vs. Priority mapping**: The exact-bug-scenario case should be Critical severity + High priority; boundary/negative cases can be Normal severity + Medium priority.
