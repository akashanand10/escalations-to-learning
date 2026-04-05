---
name: qase-api
description: "Interact with the Qase.io test management platform via its REST API (v1). Use when: querying, creating, updating, or deleting test cases, test runs, test run results, defects, suites, plans, milestones, projects, environments, and other Qase entities; searching with Qase Query Language (QQL); automating test management workflows; reporting test results."
argument-hint: "Describe what you want to do in Qase (e.g. 'list all test cases in project DEMO', 'create a test run', 'report a passed result')"
---

# Qase API (v1)

Interact with Qase.io test management from the command line using the Python REST client.

- **API Docs**: https://developers.qase.io/reference
- **Base URL**: `https://api.qase.io/v1`

## Configuration

| Setting              | Value                                  |
| -------------------- | -------------------------------------- |
| API Token env var    | `QASE_API_TOKEN`                       |
| Credentials file     | `~/.qase-credentials`                  |
| Client script        | `skills/qase-api/scripts/qase-rest.py` |
| Default project code | `DEMO`                                 |

## One-time Setup

1. Generate an API token at https://app.qase.io/user/api/token
2. Save credentials to `~/.qase-credentials`:
   ```
   QASE_API_TOKEN=<your-api-token>
   ```
3. Protect the file: `chmod 600 ~/.qase-credentials`

Or set directly: `export QASE_API_TOKEN="your-token"`

## Python REST Client

```bash
REST="skills/qase-api/scripts/qase-rest.py"
```

All commands output JSON. Pipe to `jq` for filtering. Pass `--help` to any subcommand for full options.

---

### READ Commands (safe — run freely)

**Projects**

```bash
python3 $REST list-projects --paginate
python3 $REST get-project --project DEMO
```

**Suites**

```bash
python3 $REST list-suites --project DEMO --paginate
python3 $REST get-suite --project DEMO 42
```

**Test Cases**

```bash
# List all cases
python3 $REST list-cases --project DEMO --paginate

# Filter by suite, keyword, or status (actual | draft | deprecated)
python3 $REST list-cases --project DEMO --suite-id 5 --search "login" --status actual

# Full details for one case
python3 $REST get-case --project DEMO 123
```

**Test Runs**

```bash
# List runs (status: in_progress | passed | failed | aborted)
python3 $REST list-runs --project DEMO --status in_progress

# Get a run with case IDs and defects
python3 $REST get-run --project DEMO 42 --include cases,defects
```

**Test Run Results**

```bash
# List results with filters (status: passed | failed | blocked | skipped | invalid)
python3 $REST list-results --project DEMO --run 42 --status failed --paginate

# Filter by time range
python3 $REST list-results --project DEMO \
  --from-time "2026-03-01 00:00:00" --to-time "2026-03-31 23:59:59" --paginate

# Get a specific result by hash
python3 $REST get-result --project DEMO abc123def456
```

**Defects**

```bash
python3 $REST list-defects --project DEMO --paginate
python3 $REST get-defect --project DEMO 1
```

**Milestones, Plans, Environments**

```bash
python3 $REST list-milestones --project DEMO --paginate
python3 $REST list-plans --project DEMO --paginate
python3 $REST get-plan --project DEMO 7
python3 $REST list-environments --project DEMO
```

**Custom Fields, Shared Steps, Attachments**

```bash
python3 $REST list-custom-fields --paginate
python3 $REST list-shared-steps --project DEMO --paginate
python3 $REST list-attachments --paginate
python3 $REST get-attachment abc123
```

**Users, Authors, System Fields**

```bash
python3 $REST list-users --paginate
python3 $REST list-authors --paginate
python3 $REST get-system-fields    # shows all allowed field values
```

**Search (QQL)**

```bash
python3 $REST search --query 'entity = "case" and project = "DEMO" and status = "actual"' --paginate
```

---

### WRITE Commands (confirm with user before running)

> **Duplicate check (REQUIRED before creating):** Before creating a new test case or suite, first search for existing cases/suites with similar names or coverage. Use `list-cases --search`, `list-suites`, or `search --query` to check. If a similar item already exists, present the match to the user and ask for confirmation before proceeding.

**Runs**

```bash
# Create a run with specific cases
python3 $REST create-run --project DEMO --title "Smoke v2.1" --cases 1,2,3

# Create a run with all cases
python3 $REST create-run --project DEMO --title "Full Regression" --include-all \
  --env-id 1 --milestone-id 3 --description "Release 2.1"

# Create from a test plan
python3 $REST create-run --project DEMO --title "Sprint 15" --plan-id 7

# Complete (close) a run
python3 $REST complete-run --project DEMO 42
```

**Results**

```bash
# Report a single result (status: passed | failed | blocked | skipped | invalid)
python3 $REST create-result --project DEMO --run 42 --case-id 5 \
  --status passed --time-ms 1200

# Report a failed result with defect flag
python3 $REST create-result --project DEMO --run 42 --case-id 6 --status failed \
  --comment "Login form not found" --stacktrace "ElementNotFoundError at line 42" --defect

# Bulk report from a JSON string
python3 $REST bulk-results --project DEMO --run 42 \
  --data '[{"case_id":1,"status":"passed","time_ms":1200},{"case_id":2,"status":"failed","comment":"timeout"}]'

# Bulk report from a file
python3 $REST bulk-results --project DEMO --run 42 --data @results.json
```

**Test Cases**

```bash
# severity: 1=blocker 2=critical 3=major 4=normal 5=minor 6=trivial
# priority: 1=high 2=medium 3=low
# type:     1=functional 2=smoke 3=regression 4=security 5=usability 6=performance 7=acceptance
python3 $REST create-case --project DEMO --title "User can log in" \
  --suite-id 5 --severity 2 --priority 1 --type 1
```

**Defects**

```bash
python3 $REST create-defect --project DEMO --title "Login fails" \
  --severity 2 --actual-result "500 error response"
python3 $REST resolve-defect --project DEMO 3
```

---

### DESTRUCTIVE Commands (MUST get explicit user approval before running)

```bash
python3 $REST delete-case   --project DEMO 123
python3 $REST delete-run    --project DEMO 42
python3 $REST delete-result --project DEMO abc123def456
python3 $REST delete-defect --project DEMO 3
```

---

## Output Format

| Command type                                 | Output                                   |
| -------------------------------------------- | ---------------------------------------- |
| `list-*`                                     | JSON array `[{...}, ...]` — pipe to `jq` |
| `get-*`                                      | JSON object                              |
| `create-*`                                   | JSON object (the new entity)             |
| `complete-run`, `resolve-defect`, `delete-*` | `{"status": true}`                       |

---

## Field Value Reference

### Test Case Fields

| Field             | Values                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------------- |
| `severity`        | 0=undefined, 1=blocker, 2=critical, 3=major, 4=normal, 5=minor, 6=trivial                          |
| `priority`        | 0=undefined, 1=high, 2=medium, 3=low                                                               |
| `type`            | 0=other, 1=functional, 2=smoke, 3=regression, 4=security, 5=usability, 6=performance, 7=acceptance |
| `behavior`        | 0=undefined, 1=positive, 2=negative, 3=destructive                                                 |
| `isManual`        | `true` = manual, `false` = automated                                                               |
| `isToBeAutomated` | Boolean checkbox, independent of `isManual`                                                        |
| `automation`      | Legacy field: `0` = manual, `2` = automated                                                        |
| `status`          | 0=actual, 1=draft, 2=deprecated                                                                    |

### Status Values

| Entity        | Values                                                             |
| ------------- | ------------------------------------------------------------------ |
| Run status    | `in_progress`, `passed`, `failed`, `aborted`                       |
| Result status | `passed`, `failed`, `blocked`, `skipped`, `invalid`, `in_progress` |

---

## Escalation Coverage Workflow Notes

When mapping Jira escalations to Qase coverage:

- Search titles from narrow to broad: exact phrase, then keywords, then local filtering against the full case list.
- `list-cases --search` is exact substring matching only; it is not fuzzy or semantic.
- Use suites to confirm whether a title match is in the right product area.
- Score matches explicitly and separate direct coverage from adjacent feature coverage.
- Do not suggest new cases until the user approves.
- Before creating suites or cases, run duplicate checks and show the likely overlaps.
- Link any created case back to the Jira ticket for traceability.

## Automation Audit Workflow Notes

When checking whether a Qase case is automated:

- Prefer `isManual` and `isToBeAutomated` over the legacy `automation` integer.
- Treat the codebase as the source of truth if Qase metadata and repo evidence disagree.
- Search for both numeric and project-prefixed Qase references, for example `qase(123, ...)` and `qase('ABP-123', ...)`.
- If automation exists in code, report the evidence and update Qase instead of creating duplicate Jira work.

## Common Workflows

### Create a run, report results, close it

```bash
# 1. Create run and capture its ID
RUN=$(python3 $REST create-run --project DEMO --title "Smoke v2.1" --cases 1,2,3)
RUN_ID=$(echo "$RUN" | jq '.id')

# 2. Bulk report results
python3 $REST bulk-results --project DEMO --run $RUN_ID \
  --data '[{"case_id":1,"status":"passed","time_ms":1200},{"case_id":2,"status":"passed","time_ms":800},{"case_id":3,"status":"failed","comment":"timeout"}]'

# 3. Close the run
python3 $REST complete-run --project DEMO $RUN_ID
```

### Export all test cases to a file

```bash
python3 $REST list-cases --project DEMO --paginate > all_cases.json
echo "Exported $(jq length all_cases.json) cases"
```

### Get failed results from the latest run

```bash
LATEST=$(python3 $REST list-runs --project DEMO --limit 1 | jq '.[0].id')
python3 $REST list-results --project DEMO --run $LATEST --status failed --paginate \
  | jq '.[] | {case_id, status, comment, stacktrace}'
```

### Find cases matching a keyword

```bash
python3 $REST list-cases --project DEMO --search "login" --status actual --paginate
```

---

## Rate Limits

| Scope               | Limit          |
| ------------------- | -------------- |
| Per user per minute | 1,000 requests |
| Per IP per minute   | 3,000 requests |

On HTTP 429, wait 60 seconds. For bulk writes, add `sleep 0.1` between requests.

---

## Error Handling

The client prints errors to stderr and exits with code 1 on any HTTP error.

| HTTP Code | Meaning                                     |
| --------- | ------------------------------------------- |
| 400       | Bad Request — invalid parameters or body    |
| 401       | Unauthorized — wrong or missing API token   |
| 402       | Payment Required — plan limit reached       |
| 403       | Forbidden — insufficient role permissions   |
| 404       | Not Found — entity or project doesn't exist |
| 422       | Unprocessable Entity — validation errors    |
| 429       | Too Many Requests — rate limited (wait 60s) |
| 500       | Internal Server Error — retry later         |
| 503       | Service Unavailable — maintenance window    |

---

## Guardrails

### Risk Classification

| Tier          | Risk                                            | Required behavior                                                                      |
| ------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Safe**      | Read-only                                       | Run freely, no confirmation needed                                                     |
| **Moderate**  | Creates or modifies a single entity             | Show what will be done, **ask for confirmation**                                       |
| **Dangerous** | Bulk mutation, deletion, or irreversible action | **MUST get explicit user approval**. Show affected entities first. Never auto-execute. |

### Safe (run freely)

All `list-*`, `get-*`, and `search` commands.

### Moderate (confirm before executing)

`create-run`, `complete-run`, `create-result`, `bulk-results`, `create-case`, `create-defect`, `resolve-defect`

### Dangerous (MUST get explicit user approval)

`delete-case`, `delete-run`, `delete-result`, `delete-defect` — show exactly what will be deleted and wait for "yes"/"go ahead".

### Additional Safety Rules

- **Never hardcode tokens.** Always use `QASE_API_TOKEN` from env or `~/.qase-credentials`.
- **Validate project code** before mutations — run `get-project --project CODE` first.
- **Check run status** before posting results — ensure the run is not already completed (`get-run`).

---

## Troubleshooting

- **401 Unauthorized**: Check `QASE_API_TOKEN` is set and valid. Regenerate at https://app.qase.io/user/api/token
- **403 Forbidden**: Your role lacks the required permission. Check workspace role settings.
- **404 Not Found**: Verify project code and entity ID with a `get-*` command first.
- **422 Validation Error**: The response body has field-level errors. Check required fields and value ranges.
- **429 Rate Limited**: Wait 60 seconds and retry.
- **jq not found**: `brew install jq`
- **Full API docs**: https://developers.qase.io/reference
