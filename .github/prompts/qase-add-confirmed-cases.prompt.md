---
description: "Use when: creating test cases in Qase that were approved in the escalation coverage review table on Confluence. Reads the review table, gets user confirmation, creates cases in Qase, and updates Confluence with done status and case IDs."
name: "Qase Add Confirmed Cases"
argument-hint: "Confluence page URL containing the coverage review table"
agent: "agent"
---

# Qase — Add Confirmed Test Cases from Coverage Review

Read the test coverage review table from Confluence, get user confirmation, create approved test cases in Qase, and update the Confluence page with completion status.

Use the Qase API guidance in [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md) and the Confluence REST client in [../../.agents/skills/confluence-rest/SKILL.md](../../.agents/skills/confluence-rest/SKILL.md).

## Inputs (ask the user if not provided)

| Input                                            | Required | Default                  |
| ------------------------------------------------ | -------- | ------------------------ |
| Confluence page URL or page ID (coverage review) | Yes      | —                        |
| Qase project code                                | No       | `ABP`                    |
| `Created via` custom field value                 | No       | `AI escalation context`  |

The **`Created via`** custom field (Qase field id `142`, string) is stamped on every
case created by this prompt so we can later filter / audit AI-generated cases.
Apply the default `AI escalation context` unless the user explicitly overrides it
(e.g. "set Created via to 'Manual escalation review'").

## Task

### Phase 1 — Read and Confirm

1. Fetch the Confluence page body using `get-page <ID> --body-format storage`.
2. Parse the coverage review table to extract rows where **"Add in Qase"** = `Yes`.
3. Present the list of cases to be created to the user:

```
The following test cases will be created in Qase (<PROJECT>):

| # | Suggested Case Title | Related Jira Key | Target Suite |
| - | -------------------- | ---------------- | ------------ |
| 1 | Verify ...           | BP-1234          | Bills > Create |
| ...

Proceed? (yes / no / edit)
```

4. **Wait for explicit user confirmation before creating anything.**
5. If the user says "edit", allow them to modify the list (remove cases, rename, change suite).

### Phase 2 — Duplicate Check and Create

For each approved case:

1. **Duplicate check (REQUIRED)** — Search Qase for existing cases with similar titles:
   ```bash
   python3 skills/qase-api/scripts/qase-rest.py list-cases --project ABP --search "<keywords>"
   ```
2. If a near-duplicate exists (>80% relevancy), skip creation and report the existing case.
3. If no duplicate, create the case:
   ```bash
   python3 skills/qase-api/scripts/qase-rest.py create-case --project ABP \
     --title "Verify <case title>" --suite-id <SUITE_ID> \
     --severity 2 --priority 1 --type 3 \
     --custom-field "142=AI escalation context"
   ```

   - Use `type 3` (regression) for exact bug coverage cases.
   - Use `type 1` (functional) for broader coverage cases.
   - Include the Jira ticket link in the description.
   - Always pass `--custom-field "142=<Created via value>"` using the value from
     the Inputs table (default `AI escalation context`, or the user's override).
     The flag is repeatable if more custom fields are needed.
4. Record the created Qase case ID.

### Phase 3 — Update Confluence

1. Update the coverage review table on the Confluence page:
   - Change "Add in Qase" from `Yes` to `Done ✅ — <PROJECT>-<CASE_ID>`
   - For skipped duplicates: `Skipped — duplicate of <PROJECT>-<CASE_ID>`
2. Use `update-page` to save the changes:
   ```bash
   python3 skills/confluence-rest/scripts/confluence-rest.py update-page <PAGE_ID> \
     --body @/tmp/updated-review.html
   ```

## Stop Conditions

- Do NOT create any cases without explicit user confirmation.
- Do NOT create a case if a near-duplicate already exists in Qase — report the duplicate instead.
- If the coverage review table is missing or has no rows with "Add in Qase" = `Yes`, inform the user and stop.

## Completion

- Report a summary of what was created:
  ```
  Created: 5 new cases in Qase (ABP)
  Skipped: 2 duplicates
  Confluence page updated: <URL>
  ```
- Remind the user: "When ready, use the **Qase Automation Jira Tasks** prompt to create automation tickets for approved cases."
