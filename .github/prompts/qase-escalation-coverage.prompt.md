---
description: "Use when: checking Qase coverage for one Jira escalation or a full escalation analysis report, scoring existing cases, and optionally proposing or creating missing coverage."
name: "Qase Escalation Coverage"
argument-hint: "Jira key or escalation analysis file path, plus Qase project code"
agent: "agent"
---

# Qase Test Coverage for Jira Escalations

Map engineering escalation tickets to existing Qase test coverage.

Use the shared Qase workflow guidance in [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md). When the input is a report, expect the monthly analysis format from [jira-escalation-analysis.prompt.md](./jira-escalation-analysis.prompt.md).

## Inputs

- A single Jira ticket key, or a monthly escalation analysis markdown file
- The relevant Qase project code, such as `ABP`

## Task

1. Extract the ticket key, title, issue summary, product area, and 3-5 search keywords from each escalation.
2. Search Qase for existing coverage using progressively broader matching:
   - exact phrase from the escalation summary
   - individual keywords
   - local filtering against the full case list when title search is too narrow
   - suite inspection to confirm the product area
3. Score each plausible match for relevancy on a 0-100 scale.
4. Present findings before proposing any new coverage.
5. Suggest new cases only after the user approves.
6. Create suites or cases only after the user explicitly approves creation and after duplicate checks are complete.

## Relevancy Scale

| Score Range | Meaning |
| ----------- | ------- |
| 80-100% | Directly tests the exact failure mode or regression |
| 50-79% | Covers the same feature area but not the exact bug |
| 20-49% | Only tangentially related |
| 0-19% | Keyword overlap only |

## Required Output

For a single escalation, return:

| Case ID | Title | Relevancy | Reason |
| ------- | ----- | --------- | ------ |

Then state either:

- `Coverage exists, but these gaps remain: ...`
- `No direct test coverage exists for this issue in Qase.`

If relevant cases exist with scores of 50% or higher, ask:

`Would you like me to suggest additional test cases to close the remaining gaps?`

If no relevant cases exist, ask:

`Would you like me to suggest test cases to cover this escalation?`

For a full report, return a summary table first:

| Jira Key | Title | Qase Coverage | Gaps |
| -------- | ----- | ------------- | ---- |

Then ask whether to suggest new cases for the uncovered tickets.

## Suggestion Rules

- Start with the exact bug scenario that would have caught the escalation.
- Add the root-cause edge case when it is distinct.
- Add only a small number of boundary cases.
- Keep suggestions to 3-6 cases per escalation.
- Use titles that start with `Verify`.
- Use Regression type for exact bug coverage when appropriate.

## Creation Rules

- Follow the duplicate-check and suite-hierarchy guidance in [../../.agents/skills/qase-api/SKILL.md](../../.agents/skills/qase-api/SKILL.md).
- Link every new test case back to the Jira ticket in the description.
- Do not create suites or cases until the user explicitly approves creation.