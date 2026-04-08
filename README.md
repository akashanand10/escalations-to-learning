# Copilot Prompt Workspace

This workspace packages a small set of reusable GitHub Copilot prompts for escalation analysis and Qase coverage work, plus shared skills for Jira and Qase tooling.

## What This Repo Contains

- `.github/prompts/`
  Workspace prompt files that appear in Copilot Chat and can be run from the prompt picker.
- `.agents/skills/`
  Shared workflow guidance for tool-backed tasks such as Jira via ACLI and Qase via API.
- `analysis/`
  Generated monthly and quarterly escalation analysis reports.
- `copilot-dash/`
  A local dashboard with preset queries for common analysis tasks.

## Available Prompts

- `Jira Escalation Analysis`
  Generate a monthly engineering escalation report from Jira tickets.
- `Qase Escalation Coverage`
  Map Jira escalations to Qase coverage and identify missing tests.
- `Qase Automation Check And Ticket`
  Check whether a Qase case is already automated and create a Jira tracking ticket only when needed.
- `Quarterly Escalation Analysis`
  Build a quarterly report from the monthly markdown analyses in `analysis/`.

## Prompt Recommendations

Prompt recommendations are not a separate file type. They come from:

1. Prompt files stored under `.github/prompts/`
2. The VS Code setting `chat.promptFilesRecommendations`

This repository enables that setting in `.vscode/settings.json`, so anyone opening the workspace in VS Code should get prompt recommendations automatically.

## Workspace Setup

1. Open this repository in VS Code.
2. Make sure GitHub Copilot Chat is installed and signed in.
3. Keep prompt files in `.github/prompts/`.
4. Keep reusable tool workflow guidance in `.agents/skills/`.
5. Use the chat prompt picker by typing `/` in Copilot Chat, or run `Chat: Run Prompt...` from the command palette.

## Adding New Prompt Recommendations

If someone wants to set this up in another repository, they should:

1. Create prompt files in `.github/prompts/` using the `*.prompt.md` naming convention.
2. Add clear YAML frontmatter, especially a strong `description`, plus `name` and `argument-hint` when useful.
3. Enable `chat.promptFilesRecommendations` in `.vscode/settings.json` or in user settings.
4. Keep prompts focused on one task. Move reusable multi-step tooling guidance into a skill instead of duplicating it across prompts.

Example workspace setting:

```json
{
  "chat.promptFilesRecommendations": true
}
```

## Prompt Authoring Notes

- Use prompts for a single focused task with clear inputs and outputs.
- Use skills when the workflow is broader, tool-heavy, or shared across multiple prompts.
- Put the best discovery keywords in the `description` frontmatter because that is the main surface Copilot uses to recommend a prompt.
