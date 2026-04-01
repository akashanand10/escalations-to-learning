---
description: "Use when: checking whether a Qase test case is automated in the Playwright repo, and if not, creating a Jira ticket to track the automation work. Works for a single Qase case or a batch of cases."
---

# Qase Automation Check & Jira Ticket Creation

## Purpose

For a given Qase test case, determine whether it has been automated in the Playwright repo. If not automated, create a Jira ticket to track the work and assign it to the appropriate engineer.

## Variables

All variables below are configurable. **Ask the user** to confirm or override each value before proceeding.

| Variable          | Description                                 | Default / Example                                            | Required?    |
| ----------------- | ------------------------------------------- | ------------------------------------------------------------ | ------------ |
| `QASE_PROJECT`    | Qase project code                           | `ABP`                                                        | Yes          |
| `QASE_CASE_ID`    | Numeric Qase case ID                        | `7`                                                          | Yes          |
| `JIRA_PROJECT`    | Jira project key for the ticket             | `BP`                                                         | Yes          |
| `JIRA_BOARD_JQL`  | JQL for the backlog board                   | `project = BP AND labels in (bp-velocity) ORDER BY Rank ASC` | Yes          |
| `JIRA_TYPE`       | Issue type to create                        | `Task`                                                       | Yes          |
| `JIRA_ASSIGNEE`   | Assignee email (leave blank for unassigned) | `aanand@paylocity.com`                                       | **Ask user** |
| `JIRA_LABEL`      | Label to apply to created tickets           | `bp-velocity`                                                | Yes          |
| `JIRA_PARENT`     | Parent epic/story key for the ticket        | `BP-7479`                                                    | Yes          |
| `PLAYWRIGHT_REPO` | GitHub repo for Playwright tests            | `Paylocity/Airbase.Playwright.Automation.Suite`              | Yes          |

## Prerequisites

- Qase API access configured (see `skills/qase-api/SKILL.md` for setup)
- Jira access via ACLI (see `skills/atlassian-cli/SKILL.md` for setup)
- GitHub repo access for searching the Playwright codebase

## Procedure

### Step 0: Confirm configuration with user

**Before doing anything**, ask the user to provide or confirm these values:

1. **Qase case** — Which Qase case(s) to check? (project code + case ID, e.g. `ABP-7`)
2. **Jira project** — Which Jira project to create the ticket in? (default: `BP`)
3. **Parent ticket** — Parent epic/story key? (default: `BP-7479`)
4. **Assignee** — Who should the ticket be assigned to? Enter an email, or say "unassigned" to leave it blank.
5. **Label** — Which label to apply? (default: `bp-velocity`). Don't add random labels.
6. **Issue type** — What type of Jira issue? (default: `Task`)

Proceed only after the user has confirmed. Use defaults for any value the user doesn't explicitly override.

### Step 1: Fetch Qase case details

Retrieve the test case from Qase and check its automation status.

```bash
REST=~/.agents/skills/qase-api/scripts/qase-rest.py

python3 $REST get-case --project <QASE_PROJECT> <QASE_CASE_ID>
```

**Check these fields in the response:**

- `automation` — `0` = Not Automated, `1` = To Be Automated, `2` = Automated
- `isManual` — `true` means no automation exists
- `title` — the test case name (used for the Jira summary)
- `suite_id` — helps identify the product area

If `automation == 2` (already automated), **stop here** — no ticket needed.

### Step 2: Search Playwright repo for existing automation

Even if Qase says "not automated", verify by searching the actual codebase. Tests reference Qase IDs via the `qase()` wrapper:

```ts
// Pattern in spec files:
test(qase(<CASE_ID>, 'test title'), { tag: [...] }, async () => { ... })
// or for ABP project specifically:
test(qase('ABP-<CASE_ID>', 'test title'), ...)
```

**Search the GitHub repo** for:

- `qase(<CASE_ID>` — numeric ID reference
- `qase('ABP-<CASE_ID>'` — project-prefixed reference
- Keywords from the test case title (e.g. "change vendor")

If a matching spec file is found, the test **is** automated (Qase may just not be updated). Note the file path and stop — update Qase status instead of creating a ticket.

### Step 3: Create Jira ticket (if not automated)

If Steps 1 and 2 both confirm no automation exists, create the Jira ticket:

```bash
ACLI="/Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli"

# With assignee:
$ACLI jira workitem create \
  --project "<JIRA_PROJECT>" \
  --type "<JIRA_TYPE>" \
  --summary "Automate Qase test <QASE_PROJECT>-<QASE_CASE_ID>: <test case title>" \
  --description "Qase Test Case: <QASE_PROJECT>-<QASE_CASE_ID> (https://app.qase.io/case/<QASE_PROJECT>-<QASE_CASE_ID>)

Title: <test case title>

Current Status: Manual test (not automated)

Acceptance Criteria:
- Create a Playwright spec that covers the scenario described in <QASE_PROJECT>-<QASE_CASE_ID>
- Link the test to Qase using qase('<QASE_PROJECT>-<QASE_CASE_ID>', 'test title') wrapper
- Update the Qase case automation status to Automated once the spec is merged" \
  --assignee "<JIRA_ASSIGNEE>" \
  --parent "<JIRA_PARENT>"

# Without assignee (if user chose unassigned):
$ACLI jira workitem create \
  --project "<JIRA_PROJECT>" \
  --type "<JIRA_TYPE>" \
  --summary "Automate Qase test <QASE_PROJECT>-<QASE_CASE_ID>: <test case title>" \
  --description "...same as above..." \
  --parent "<JIRA_PARENT>"
```

### Step 4: Add label to the ticket

```bash
$ACLI jira workitem edit --key "<TICKET_KEY>" --labels "<JIRA_LABEL>"
```

### Step 5: Confirm on the board

The ticket should now appear in the backlog using the board query:

```
project = BP AND labels in (bp-velocity) ORDER BY Rank ASC
```

Board URL: https://paylocity.atlassian.net/jira/software/c/projects/BP/boards/1331/backlog

## Batch Mode

To check multiple Qase cases at once, repeat Steps 1–4 for each case ID. Collect results in a summary table:

| Qase Case | Title                                           | Automated? | Jira Ticket |
| --------- | ----------------------------------------------- | ---------- | ----------- |
| ABP-7     | Verify user should be able to change the vendor | No         | BP-8031     |

## Qase Project Code Reference

| Qase Code | Domain                               |
| --------- | ------------------------------------ |
| `ABP`     | Bill Payments                        |
| `AAE`     | Admin Experience                     |
| `ACE`     | Cards                                |
| `AEM`     | Expense Management                   |
| `AGP`     | Guided Procurement + Purchase Orders |
| `AVM`     | Vendor Management                    |
