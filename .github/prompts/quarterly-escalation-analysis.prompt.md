---
description: "Use when: generating a quarterly engineering escalation report from monthly analysis files, including hotspot counts, trends, and recommendations."
name: "Quarterly Escalation Analysis"
argument-hint: "Quarter and year, or explicit monthly analysis file paths"
agent: "agent"
---

# Quarterly Engineering Escalation Analysis

Generate a quarterly engineering escalation report from the monthly markdown analyses in `analysis/`.

Monthly files should follow the structure produced by [jira-escalation-analysis.prompt.md](./jira-escalation-analysis.prompt.md).

## Inputs

- A quarter and year, or an explicit list of monthly analysis files
- Optional report filename override

## Task

1. Identify the monthly analysis files for the requested quarter.
2. If any month is missing, note the gap and continue with the available files.
3. Read each escalation and assign a primary product area when needed.
4. Aggregate counts by month, product area, customer, and owner.
5. Write a markdown report under `analysis/` named `bp-engineering-escalations-Q<N>-<year>-analysis.md` unless the user specifies a different filename.

## Product Area Guidance

Use the most specific primary area that fits. Common areas include:

- Bills (Create/Edit)
- Bills (Approval/POA)
- Bills (Recurring)
- Inbox / Scanning
- Payments
- Vendor Credits
- Tags / Line Items
- Bulk Operations
- Drafts / Visibility
- Infrastructure / Platform
- Data Migration

If a ticket clearly spans two areas, use the primary area in the monthly breakdown and mention the secondary overlap in the narrative.

## Output Format

Follow this structure:

```markdown
# <Project> Engineering Escalations - Quarterly Report (Q<N> <Year>)

## Overview

| Month             | Total Tickets |
| ----------------- | ------------- |
| <Month 1>         | <count>       |
| <Month 2>         | <count>       |
| <Month 3>         | <count>       |
| **Quarter Total** | **<total>**   |

## Escalations by Product Area

| Product Area | Count | Tickets |
| ------------ | ----- | ------- |
| ...          | ...   | ...     |

## Hotspots & Patterns

Narrative summary of volume, trends, repeat customers, repeat root causes, and owner load.

## Monthly Breakdown

### <Month 1>

| #   | Key | Summary | Product Area | Priority | Status | Owner |
| --- | --- | ------- | ------------ | -------- | ------ | ----- |

## Recommendations

- Areas that need engineering investment
- Process improvements
- Monitoring or alerting gaps
```

## Requirements

- Sort the product-area table by count descending.
- Use Jira browse links in the form `https://paylocity.atlassian.net/browse/<KEY>`.
- Count each ticket once in the quarter total, even if the narrative mentions cross-area overlap.
- Keep the hotspot narrative evidence-based and tied to the monthly files.
