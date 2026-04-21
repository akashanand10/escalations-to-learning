---
description: "Use when: creating Jira automation tasks for test cases that were marked 'Create Jira Task for Automation = Yes' in the Confluence coverage review table. Asks for assignee and board, creates Jira tasks, and updates Confluence with ticket links and done status."
name: "Qase Automation Jira Tasks"
argument-hint: "Confluence page URL containing the coverage review table"
agent: "agent"
---

# Create Jira Automation Tasks from Coverage Review

Read the test coverage review table from Confluence, get user confirmation on which cases to automate, create Jira tasks, and update the Confluence page with ticket links.

Use the Jira REST client in [../../.agents/skills/jira-rest-api/SKILL.md](../../.agents/skills/jira-rest-api/SKILL.md) and the Confluence REST client in [../../.agents/skills/confluence-rest/SKILL.md](../../.agents/skills/confluence-rest/SKILL.md).

## Inputs (ask the user if not provided)

| Input                                            | Required | Default                              |
| ------------------------------------------------ | -------- | ------------------------------------ |
| Confluence page URL or page ID (coverage review) | Yes      | —                                    |
| Jira project key                                 | No       | `BP`                                 |
| Jira parent issue key                            | No       | `BP-7479`                            |
| Jira label                                       | No       | `bp-velocity`                        |
| Jira issue type                                  | No       | `Task`                               |
| Assignee                                         | Yes      | — (ask the user; allow `unassigned`) |
| Jira board / sprint                              | Yes      | — (ask the user)                     |

## Task

### Phase 1 — Read and Confirm

1. Fetch the Confluence page body using `get-page <ID> --body-format storage`.
2. Parse the coverage review table to extract rows where **"Create Jira Task for Automation"** = `Yes`.
3. Ask the user:
   - **"Who should these automation tasks be assigned to?"** (allow `unassigned`)
   - **"Which Jira board/project should they be added under?"**
4. Present the list of tasks to be created:

```
The following Jira automation tasks will be created:

| # | Case Title | Qase ID | Assignee | Project |
| - | ---------- | ------- | -------- | ------- |
| 1 | Verify ... | ABP-123 | user@co  | BP      |
| ...

Proceed? (yes / no / edit)
```

5. **Wait for explicit user confirmation before creating anything.**

### Phase 2 — Create Jira Tasks

For each approved case:

1. Create a Jira task:
   ```bash
   python3 .agents/skills/jira-rest-api/scripts/jira-rest-client.py create \
     --project BP \
     --type Task \
     --summary "Automate Qase test <PROJECT>-<CASE_ID>: <case title>" \
     --description "Automate the following Qase test case:\n\nQase: https://app.qase.io/case/<PROJECT>-<CASE_ID>\n\nAcceptance Criteria:\n- Create Playwright automation for this test case\n- Link with qase('<PROJECT>-<CASE_ID>') wrapper\n- Update Qase automation status after merge" \
     --parent <PARENT_KEY> \
     --labels <LABEL>
   ```
2. Assign the issue if an assignee was specified:
   ```bash
   python3 .agents/skills/jira-rest-api/scripts/jira-rest-client.py assign <ISSUE_KEY> --user "<assignee>"
   ```
3. Record the created Jira issue key.

### Phase 3 — Update Confluence

1. Update the coverage review table on the Confluence page:
   - Change "Create Jira Task for Automation" from `Yes` to `Done ✅ — <ISSUE_KEY>`
   - Include a Jira browse link: `https://paylocity.atlassian.net/browse/<ISSUE_KEY>`
2. Use `update-page` to save the changes:
   ```bash
   python3 skills/confluence-rest/scripts/confluence-rest.py update-page <PAGE_ID> \
     --body @/tmp/updated-review.html
   ```

## Ticket Rules

- Summary format: `Automate Qase test <PROJECT>-<CASE_ID>: <case title>`
- Include the Qase case link in the description.
- Include acceptance criteria: create automation, link to Qase with `qase(...)` wrapper, update Qase status after merge.
- If the user chose `unassigned`, create the issue without an assignee.
- Apply the configured Jira label after ticket creation.

## Stop Conditions

- Do NOT create any Jira tasks without explicit user confirmation.
- If the coverage review table has no rows with "Create Jira Task for Automation" = `Yes`, inform the user and stop.
- If the Qase case ID column is empty (cases not yet created), warn the user to run the **Qase Add Confirmed Cases** step first.

## Completion

- Report a summary:
  ```
  Created: 5 Jira automation tasks
  Assignee: user@company.com
  Project: BP (parent: BP-7479)
  Confluence page updated: <URL>
  ```
- Output the Confluence page URL.
