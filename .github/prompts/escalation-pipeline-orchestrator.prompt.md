---
description: "Use when: running the full escalation management pipeline end-to-end — from Jira analysis through Confluence documentation, Qase test coverage review, case creation, and automation task creation. Orchestrates all steps with user confirmations between each phase. Confluence is the single source of truth throughout."
name: "Escalation Pipeline Orchestrator"
argument-hint: "Month/year and Confluence space key to start, or 'resume' with a Confluence page URL to pick up mid-pipeline"
agent: "agent"
---

# Escalation Pipeline Orchestrator

Run the full escalation management pipeline end-to-end. Each phase saves its output to Confluence, which serves as the single documentation hub throughout.

This orchestrator chains the following prompts in sequence, with user confirmation gates between each phase:

1. **Jira Escalation Analysis → Confluence** — [jira-escalation-to-confluence.prompt.md](./jira-escalation-to-confluence.prompt.md)
2. **Monthly Escalation Data Summary** — [monthly-escalation-summary.prompt.md](./monthly-escalation-summary.prompt.md)
3. **Escalation Test Coverage Review** — [escalation-test-coverage-review.prompt.md](./escalation-test-coverage-review.prompt.md)
4. **Qase Add Confirmed Cases** — [qase-add-confirmed-cases.prompt.md](./qase-add-confirmed-cases.prompt.md)
5. **Qase Automation Jira Tasks** — [qase-automation-jira-tasks.prompt.md](./qase-automation-jira-tasks.prompt.md)

Use the shared skills:

- [../../.agents/skills/jira-rest-api/SKILL.md](../../.agents/skills/jira-rest-api/SKILL.md)
- [../../.agents/skills/confluence-rest/SKILL.md](../../.agents/skills/confluence-rest/SKILL.md)
- [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md)

## Inputs (collect upfront)

| Input                                                                  | Required | Default     |
| ---------------------------------------------------------------------- | -------- | ----------- |
| Month and year (or JQL)                                                | Yes      | —           |
| Jira project key                                                       | No       | `BP`        |
| Confluence space key or space ID                                       | Yes      | —           |
| Confluence parent page ID                                              | No       | Space root  |
| Qase project code                                                      | No       | `ABP`       |
| Resume mode? (provide existing Confluence URL to skip completed steps) | No       | Start fresh |

Ask the user for all required inputs before starting. Collect them in a single prompt to minimize back-and-forth.

## Pipeline Execution

### Shared State

Maintain these variables across all phases:

- `CONFLUENCE_PAGE_ID` — the main escalation analysis page
- `CONFLUENCE_PAGE_URL` — shareable link
- `SUMMARY_PAGE_ID` — the summary analytics page
- `REVIEW_PAGE_ID` — the coverage review page (may be the same as main or a child page)
- `SPACE_ID` — Confluence space
- `JIRA_PROJECT` — Jira project key
- `QASE_PROJECT` — Qase project code

---

### Phase 1: Jira Escalation Analysis → Confluence

**Goal**: Query Jira for escalation tickets and publish the full analysis to Confluence.

Follow the instructions in [jira-escalation-to-confluence.prompt.md](./jira-escalation-to-confluence.prompt.md).

**On completion**:

- Store `CONFLUENCE_PAGE_ID` and `CONFLUENCE_PAGE_URL`
- Tell the user: **"✅ Phase 1 complete. Escalation analysis published: <URL>"**
- Ask: **"Proceed to Phase 2 (Monthly Summary)? (yes / skip / stop)"**

---

### Phase 2: Monthly Escalation Data Summary

**Goal**: Generate analytics from the escalation report and publish a summary page.

Follow the instructions in [monthly-escalation-summary.prompt.md](./monthly-escalation-summary.prompt.md), passing `CONFLUENCE_PAGE_ID` as the source.

**On completion**:

- Store `SUMMARY_PAGE_ID`
- Tell the user: **"✅ Phase 2 complete. Summary published: <URL>"**
- Ask: **"Proceed to Phase 3 (Test Coverage Review)? (yes / skip / stop)"**

---

### Phase 3: Escalation Test Coverage Review

**Goal**: Check Qase for existing test coverage and propose new cases.

Follow the instructions in [escalation-test-coverage-review.prompt.md](./escalation-test-coverage-review.prompt.md), passing `CONFLUENCE_PAGE_ID` as the source.

**On completion**:

- Store `REVIEW_PAGE_ID`
- Present the coverage review table to the user for review
- Tell the user: **"✅ Phase 3 complete. Coverage review saved: <URL>"**
- Ask: **"Review the table above. Adjust any 'Yes'/'No' values, then say 'proceed' to create the approved Qase cases, 'skip' to move to automation tasks, or 'stop' to end."**

---

### Phase 4: Create Confirmed Qase Cases

**Goal**: Create the approved test cases in Qase and update Confluence.

Follow the instructions in [qase-add-confirmed-cases.prompt.md](./qase-add-confirmed-cases.prompt.md), passing `REVIEW_PAGE_ID` as the source.

**On completion**:

- Tell the user: **"✅ Phase 4 complete. Qase cases created. Confluence updated: <URL>"**
- Ask: **"Do these test cases need to be automated? (yes / no)"**
  - If **no** → Skip Phase 5, go to completion.
  - If **yes** → Proceed to Phase 5.

---

### Phase 5: Create Jira Automation Tasks

**Goal**: Create Jira tasks for automating the approved test cases and update Confluence.

Follow the instructions in [qase-automation-jira-tasks.prompt.md](./qase-automation-jira-tasks.prompt.md), passing `REVIEW_PAGE_ID` as the source.

Before starting, ask the user:

- **"Who should the automation tasks be assigned to?"**
- **"Which Jira board/project should they be added under?"**

**On completion**:

- Tell the user: **"✅ Phase 5 complete. Jira automation tasks created. Confluence updated: <URL>"**

---

## Resume Mode

If the user provides an existing Confluence page URL with "resume":

1. Fetch the page and inspect its content to determine which phases have been completed.
2. Look for these markers:
   - Escalation analysis content → Phase 1 done
   - Summary analytics section/child page → Phase 2 done
   - Coverage review table → Phase 3 done
   - "Done ✅" markers in "Add in Qase" column → Phase 4 done
   - "Done ✅" markers in "Create Jira Task" column → Phase 5 done
3. Start from the first incomplete phase.
4. Ask the user to confirm: **"It looks like Phases 1-<N> are complete. Start from Phase <N+1>?"**

## User Confirmation Gates

Every phase transition requires user input. Valid responses at each gate:

| Response          | Action                                            |
| ----------------- | ------------------------------------------------- |
| `yes` / `proceed` | Run the next phase                                |
| `skip`            | Skip the next phase and move to the one after     |
| `stop`            | End the pipeline; summarize what was completed    |
| `edit`            | Allow the user to modify inputs before proceeding |

## Pipeline Completion

When all phases are done (or the user stops early), output a final summary:

```
Pipeline Summary
================
Phase 1 — Escalation Analysis:    ✅ <URL>
Phase 2 — Monthly Summary:        ✅ <URL>
Phase 3 — Coverage Review:        ✅ <URL>
Phase 4 — Qase Cases Created:     ✅ <count> cases
Phase 5 — Jira Automation Tasks:  ✅ <count> tasks

All documentation is on Confluence: <MAIN_URL>
```

For skipped phases, show `⏭️ Skipped`. For incomplete phases, show `⏸️ Not started`.
