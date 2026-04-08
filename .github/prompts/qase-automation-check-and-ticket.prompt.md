---
description: "Use when: checking whether Qase cases are already automated in the Playwright repo and, if not, creating Jira tracking tickets with the approved defaults."
name: "Qase Automation Check And Ticket"
argument-hint: "Qase case ID or IDs, with optional Jira overrides"
agent: "agent"
---

# Qase Automation Check and Jira Ticket Creation

Check whether one or more Qase cases are already automated, and create Jira tracking tickets only when automation does not already exist.

Use the Qase API guidance in [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md) and the Jira ticket creation guidance in [../../.agents/skills/atlassian-cli/SKILL.md](../../.agents/skills/atlassian-cli/SKILL.md).

## Required Confirmation

Before doing any work, confirm or collect these values from the user. If they do not override a value, use the default.

| Variable            | Default                                         |
| ------------------- | ----------------------------------------------- |
| Qase project        | `ABP`                                           |
| Qase case ID or IDs | none                                            |
| Jira project        | `BP`                                            |
| Jira parent         | `BP-7479`                                       |
| Jira label          | `bp-velocity`                                   |
| Jira issue type     | `Task`                                          |
| Jira assignee       | ask the user; allow `unassigned`                |
| Playwright repo     | `Paylocity/Airbase.Playwright.Automation.Suite` |

## Task

1. Fetch each Qase case and inspect automation metadata.
2. Prefer `isManual` and `isToBeAutomated` over the legacy integer field.
3. Search the Playwright repo for existing automation using:
   - `qase('<PROJECT>-<CASE_ID>'`
   - `qase(<CASE_ID>,`
   - distinctive title keywords
4. If a matching spec already exists, stop for that case and report the file path instead of creating Jira work.
5. If no matching automation exists, create a Jira ticket using the approved configuration.
6. Apply the requested Jira label after ticket creation.

## Ticket Rules

- Use the summary format `Automate Qase test <PROJECT>-<CASE_ID>: <case title>`.
- Include the Qase case link in the description.
- Include acceptance criteria that require creating the automation, linking it back to Qase with the `qase(...)` wrapper, and updating Qase status after merge.
- If the user chose `unassigned`, create the Jira issue without an assignee.

## Stop Conditions

- If the case is already automated in code, do not create a Jira ticket.
- If the case metadata is ambiguous, report the ambiguity before creating Jira work.

## Batch Output

When checking multiple cases, return:

| Qase Case | Title | Automated? | Evidence | Jira Ticket |
| --------- | ----- | ---------- | -------- | ----------- |

Use `Evidence` for the matching spec path or the reason no automation was found.
