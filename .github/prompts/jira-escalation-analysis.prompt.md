---
description: "Use when: generating a monthly engineering escalation analysis from Jira tickets, including issue summaries, product area classification, update timelines, and next actions."
name: "Jira Escalation Analysis"
argument-hint: "Project/date range or JQL for the escalation report"
agent: "agent"
---

# Jira Engineering Escalation Analysis

Generate a monthly engineering escalation analysis report from Jira work items.

Use the shared Jira tooling and command patterns documented in [../../.agents/skills/atlassian-cli/SKILL.md](../../.agents/skills/atlassian-cli/SKILL.md), especially the search-plus-detail scripts for Jira and the REST backup flow when ACLI authentication fails.

## Inputs

- A Jira project key and month/year, or an explicit JQL query
- Optional report filename override

If the user gives only a month/year, build a JQL like:

```jql
created >= "2026-03-01" AND project = BP AND type = "Engineering Escalation" AND created <= "2026-03-31" ORDER BY key DESC
```

## Task

1. Query Jira for engineering escalation tickets in the requested range.
2. Fetch full details for every result, including reporter, assignee, comments, and timestamps.
3. Infer a primary product area for each ticket from the summary and comment history.
4. Write a markdown analysis file under `analysis/` named `bp-engineering-escalations-<month>-<year>-analysis.md` unless the user specifies a different name.

## Product Area Classification

Use the most specific product area that fits. Common areas include:

- Bills (Create/Edit/Approval/POA/Recurring)
- Inbox / Scanning / Uploads
- Payments / Approvals / Notifications
- Vendor Credits
- Drafts / Visibility / Permissions
- Bulk Operations / Imports
- Tags / Line Items / Ledger
- Infrastructure / Platform
- Data Migration

Do not force tickets into only these buckets. Add a new product area when the pattern is materially different.

## Output Format

Follow this structure. See `analysis/bp-engineering-escalations-march-2026-analysis.md` for an example of the finished report style.

````markdown
# <Project> Engineering Escalations Analysis (<Month Year>)

Query used:

\```jql
<the JQL query used>
\```

Total tickets found: <count>

Note: Update history below is based on ticket creation metadata and comment timelines from Jira.

Issue: https://paylocity.atlassian.net/browse/<KEY> — <summary without customer prefix>

Customer/Account: <customer name> (Prod)

Product Area: <inferred product area>

Priority: <priority> | Status: <status> | Owner: <assignee>

Issue Summary: <1-2 sentence summary of the issue, root cause, and resolution or current state>

Updates:

- ticket created by <reporter> on <created YYYY-MM-DD>
- <chronological comment summaries>

Next action: <concrete next step based on latest state>; Owner: <assignee>

---
````

## Per-ticket Rules

1. Strip the `[CustomerName]` prefix from the Jira summary and place it in `Customer/Account`.
2. If no customer prefix exists, use `Not specified (Prod)` unless the ticket explicitly indicates a different environment.
3. Keep updates chronological and skip low-signal noise, duplicate acknowledgements, and bot chatter.
4. If there are no meaningful comments, write `no comments yet`.
5. Match the depth of the issue summary to the ticket complexity; keep it concise but specific.
6. For `Done` tickets, the next action should be a monitoring or verification follow-up rather than additional implementation work.
7. Preserve Jira ordering, typically key descending unless the user requested a different sort.

## Completion Criteria

- The final markdown file exists in `analysis/`
- Each ticket has a product area, issue summary, update timeline, and next action
- The report includes the exact JQL used and the total ticket count