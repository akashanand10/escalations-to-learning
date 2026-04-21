---
description: "Use when: reviewing Qase test coverage for escalation issues documented in a Confluence page. Searches Qase for existing coverage, scores relevancy, and proposes new cases in a tabular format with 'Add in Qase' and 'Create Jira Task for Automation' columns. Saves the review table back to Confluence."
name: "Escalation Test Coverage Review"
argument-hint: "Confluence page URL of the escalation report, plus optional Qase project code"
agent: "agent"
---

# Escalation Test Coverage Review

Read escalation issues from a Confluence page, check Qase for existing test coverage, score relevancy, and propose new test cases. Save the coverage review table back to Confluence.

Use the Qase API guidance in [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md) and the Confluence REST client in [../../.agents/skills/confluence-rest/SKILL.md](../../.agents/skills/confluence-rest/SKILL.md).

## Inputs (ask the user if not provided)

| Input                                              | Required | Default              |
| -------------------------------------------------- | -------- | -------------------- |
| Confluence page URL or page ID (escalation report) | Yes      | —                    |
| Qase project code                                  | No       | `ABP`                |
| Confluence space/parent for the review page        | No       | Same space as source |

## Task

### Phase 1 — Extract Escalations

1. Fetch the Confluence page body using `get-page <ID> --body-format storage`.
2. Parse each escalation to extract: Jira key, title, issue summary, product area, and 3-5 search keywords.

### Phase 2 — Search Qase for Existing Coverage

For each escalation:

1. Search Qase using progressively broader matching:
   - Exact phrase from the escalation summary
   - Individual keywords
   - Local filtering against the full case list when title search is too narrow
   - Suite inspection to confirm the product area
2. Score each plausible match on the relevancy scale below.

### Phase 3 — Build the Coverage Review Table

For each escalation, produce a row with:

| Jira Key | Title | Existing Qase Coverage | Relevancy Score | Suggested New Cases | Add in Qase | Create Jira Task for Automation |
| -------- | ----- | ---------------------- | --------------- | ------------------- | ----------- | ------------------------------- |

Column definitions:

- **Existing Qase Coverage** — Case IDs and titles of matching Qase cases (or "None found")
- **Relevancy Score** — Highest score among matching cases (0-100%), or "N/A" if none
- **Suggested New Cases** — Proposed test case titles to close coverage gaps (3-6 per escalation)
- **Add in Qase** — `Yes` or `No` — whether the suggested cases should be created in Qase
- **Create Jira Task for Automation** — `Yes` or `No` — whether a Jira automation task should be created

Default both action columns to `Yes` when no relevant coverage exists (relevancy < 50%).
Default both to `No` when strong coverage exists (relevancy >= 80%).
For partial coverage (50-79%), default "Add in Qase" to `Yes` and "Create Jira Task" to `Yes`.

### Phase 4 — Save to Confluence

1. Format the table as Confluence HTML storage format.
2. Either:
   - **Append** a "Test Coverage Review" section to the existing escalation page, OR
   - **Create a child page** titled `<Parent Title> — Test Coverage Review`
3. Share the Confluence page URL.

## Relevancy Scale

| Score Range | Meaning                                             |
| ----------- | --------------------------------------------------- |
| 80-100%     | Directly tests the exact failure mode or regression |
| 50-79%      | Covers the same feature area but not the exact bug  |
| 20-49%      | Only tangentially related                           |
| 0-19%       | Keyword overlap only                                |

## Suggestion Rules

- Start with the exact bug scenario that would have caught the escalation.
- Add the root-cause edge case when it is distinct.
- Add only a small number of boundary cases.
- Keep suggestions to 3-6 cases per escalation.
- Use titles that start with `Verify`.
- Use Regression type for exact bug coverage.

## Important

- This prompt **does NOT create** any Qase cases or Jira tickets. It only proposes.
- The user must review the table and adjust `Yes`/`No` values before proceeding to the next steps.
- Present the table to the user for review before saving to Confluence.

## Completion

- Present the coverage review table in chat for user review.
- After user approval, save to Confluence.
- Output: **"Coverage review saved to Confluence: <URL>"**
- Remind the user: "Review the 'Add in Qase' and 'Create Jira Task' columns. When ready, use the **Qase Add Confirmed Cases** prompt to create the approved cases."
