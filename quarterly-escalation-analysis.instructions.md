---
description: "Use when: producing a quarterly summary of engineering escalations from monthly analysis docs. Covers aggregating monthly reports, identifying hotspots by product area, and generating a quarterly scorecard."
---

# Quarterly Engineering Escalation Analysis

## Purpose

Summarise monthly escalation analysis docs (e.g. `analysis/bp-engineering-escalations-<month>-<year>-analysis.md`) into a single quarterly report. The goal is to surface **hotspots** — product areas with recurring or high-volume escalations — and track trends across the quarter.

## Input

Monthly analysis markdown files for each month in the quarter. Each file follows the format defined in `jira-ticket-analysis.instructions.md` and contains per-ticket entries with:

- Issue key + link + summary
- Customer/Account
- Priority, Status, Owner
- Update timeline and next actions

## Procedure

### Step 1: Collect monthly files

Identify all monthly analysis files for the target quarter. For example, Q1 2026:

- `analysis/bp-engineering-escalations-january-2026-analysis.md`
- `analysis/bp-engineering-escalations-february-2026-analysis.md`
- `analysis/bp-engineering-escalations-march-2026-analysis.md`

### Step 2: Classify each ticket by product area

Read every ticket in each monthly file. Assign a product area based on the issue summary, description, and comments. Common product areas (non-exhaustive — add new ones as they emerge):

| Product Area              | Keywords / Signals                                          |
| ------------------------- | ----------------------------------------------------------- |
| Bills (Create/Edit)       | bill create, bill edit, save bill, pending bill             |
| Bills (Approval/POA)      | bill approval, POA, approve, approval error                 |
| Bills (Recurring)         | recurring bill, approver on recurring                       |
| Inbox / Scanning          | inbox, email upload, scan, OCR, Veryfi, not appearing       |
| Payments                  | payment, payment approval, payment failed, initiate payment |
| Vendor Credits            | vendor credit, credit memo, credit upload                   |
| Tags / Line Items         | tags, line items, ledger                                    |
| Bulk Operations           | bulk upload, bulk import, timeout                           |
| Drafts / Visibility       | draft, visibility, permission scope                         |
| Infrastructure / Platform | Cloudflare, WAF, worker, timeout, R15, memory               |
| Data Migration            | migration, migrated, legacy data                            |

### Step 3: Build the quarterly summary

Produce a markdown file named `analysis/bp-engineering-escalations-Q<N>-<year>-analysis.md` with the following structure:

```markdown
# <Project> Engineering Escalations — Quarterly Report (Q<N> <Year>)

## Overview

| Month             | Total Tickets |
| ----------------- | ------------- |
| <Month 1>         | <count>       |
| <Month 2>         | <count>       |
| <Month 3>         | <count>       |
| **Quarter Total** | **<total>**   |

## Escalations by Product Area

| Product Area         | Count | Tickets                               |
| -------------------- | ----- | ------------------------------------- |
| Bills (Approval/POA) | 4     | [BP-1234](link), [BP-1235](link), ... |
| Payments             | 3     | [BP-1240](link), [BP-1241](link), ... |
| ...                  | ...   | ...                                   |

Sort by count descending. This is the primary hotspot table.

## Hotspots & Patterns

Narrative section summarising:

- Which product areas have the highest escalation volume
- Whether any area is trending up or down across months
- Repeat customers (same customer appearing in multiple escalations)
- Repeat root causes (e.g. Cloudflare/WAF blocking uploads appeared twice in March)
- Owner load distribution — who is handling the most escalations

## Monthly Breakdown

### <Month 1>

| #   | Key             | Summary    | Product Area | Priority | Status | Owner |
| --- | --------------- | ---------- | ------------ | -------- | ------ | ----- |
| 1   | [BP-XXXX](link) | Short desc | Area         | High     | Done   | Name  |
| ... | ...             | ...        | ...          | ...      | ...    | ...   |

### <Month 2>

(same table format)

### <Month 3>

(same table format)

## Recommendations

Based on hotspot analysis, suggest:

- Areas that may need dedicated engineering investment
- Process improvements (e.g. duplicate-check gaps, OCR reliability)
- Monitoring/alerting gaps revealed by escalation patterns
```

## Notes

- If a monthly file is missing, note the gap in the report and proceed with available data.
- A ticket may belong to more than one product area; pick the primary one. If genuinely dual, list it under both but count it once in the total.
- Use the Jira browse URL format `https://paylocity.atlassian.net/browse/<KEY>` for links.
