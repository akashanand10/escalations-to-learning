---
description: "Use when: generating a monthly escalation data summary with analytics — issue counts, product area breakdown, priority distribution, patterns, and trends. Reads from a Confluence escalation report and saves the summary back to Confluence."
name: "Monthly Escalation Data Summary"
argument-hint: "Confluence page URL or ID of the escalation analysis report"
agent: "agent"
---

# Monthly Escalation Data Summary

Generate analytics and a summary from an existing escalation analysis Confluence page and publish the summary back to Confluence.

Use the Confluence REST client in [../../.agents/skills/confluence-rest/SKILL.md](../../.agents/skills/confluence-rest/SKILL.md) and the Jira REST client in [../../.agents/skills/jira-rest-api/SKILL.md](../../.agents/skills/jira-rest-api/SKILL.md) if additional Jira data is needed.

## Inputs (ask the user if not provided)

| Input                                                     | Required | Default                                             |
| --------------------------------------------------------- | -------- | --------------------------------------------------- |
| Confluence page URL or page ID (source escalation report) | Yes      | —                                                   |
| Confluence space key or space ID (for summary page)       | No       | Same space as source                                |
| Parent page ID for the summary                            | No       | Same parent as source                               |
| Summary page title override                               | No       | Auto: `<Project> Escalation Summary — <Month Year>` |

## Task

1. **Collect inputs** — Ask the user for the Confluence page URL/ID of the escalation report. Ask for any other missing inputs.
2. **Read the escalation report** — Fetch the Confluence page body using `get-page <ID> --body-format storage`.
3. **Parse and extract** — Extract each escalation's Jira key, summary, product area, priority, status, owner, and customer.
4. **Compute analytics** — Generate the following metrics:
   - Total issue count
   - Breakdown by product area (count + percentage)
   - Breakdown by priority (count + percentage)
   - Breakdown by status (Open / In Progress / Done / etc.)
   - Owner load distribution
   - Repeat customers (customers with > 1 escalation)
   - Average time-to-resolution (if data available)
5. **Identify patterns** — Look for:
   - Product areas with increasing trend vs previous months (if data available)
   - Clusters of related issues
   - Recurring root causes
   - Common customers
6. **Build summary page** — Format as Confluence HTML storage format.
7. **Create Confluence page** — Publish the summary as a new page.
8. **Share link** — Output the Confluence page URL.

## Output Structure (Confluence HTML)

### 1. Overview

| Metric            | Value               |
| ----------------- | ------------------- |
| Total Escalations | `<count>`           |
| Date Range        | `<start>` — `<end>` |
| Unique Customers  | `<count>`           |

### 2. Escalations by Product Area

| Product Area | Count | % of Total |
| ------------ | ----- | ---------- |
| ...          | ...   | ...        |

Sort by count descending.

### 3. Priority Distribution

| Priority | Count | % of Total |
| -------- | ----- | ---------- |
| Critical | ...   | ...        |
| High     | ...   | ...        |
| Medium   | ...   | ...        |
| Low      | ...   | ...        |

### 4. Status Breakdown

| Status      | Count |
| ----------- | ----- |
| Done        | ...   |
| In Progress | ...   |
| Open        | ...   |

### 5. Owner Load

| Owner | Assigned Issues |
| ----- | --------------- |
| ...   | ...             |

### 6. Repeat Customers

| Customer | Escalation Count | Tickets |
| -------- | ---------------- | ------- |

### 7. Patterns & Observations

Narrative section covering:

- Hotspot product areas
- Trending issues
- Root cause clusters
- Recommendations

### 8. Issue Index

| #   | Jira Key | Summary | Product Area | Priority | Status | Owner |
| --- | -------- | ------- | ------------ | -------- | ------ | ----- |

Include Jira browse links in the format `https://paylocity.atlassian.net/browse/<KEY>`.

## Confluence Page Creation

```bash
python3 skills/confluence-rest/scripts/confluence-rest.py create-page \
  --space-id <SPACE_ID> \
  --parent-id <PARENT_ID> \
  --title "<Project> Escalation Summary — <Month Year>" \
  --body @/tmp/escalation-summary.html
```

## Completion

- Confirm the Confluence page was created successfully.
- Output: **"Escalation summary published to Confluence: <URL>"**
