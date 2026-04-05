---
name: atlassian-cli
description: "Use Atlassian CLI (acli) to interact with Jira and Confluence from the terminal. Use when: creating, editing, searching, or transitioning Jira work items; managing sprints, boards, and projects; viewing or creating Confluence pages and blog posts; querying Jira with JQL; bulk operations on issues; engineering escalation analysis; automating Atlassian workflows."
argument-hint: "Describe what you want to do in Jira or Confluence (e.g. 'create a bug in PROJECT', 'search for my open issues')"
---

# Atlassian CLI (acli)

Interact with Jira Cloud and Confluence Cloud from the command line using the Atlassian CLI.

## Configuration

> **Update these placeholders** to match your environment.

| Setting         | Value                                                  |
| --------------- | ------------------------------------------------------ |
| Binary path     | `/Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli` |
| Default project | `MYPROJECT`                                            |
| Default site    | `paylocity.atlassian.net`                              |
| Default email   | `aanand@paylocity.com`                                 |

## Setup

Set the shell variable before running commands:

```bash
ACLI="/Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli"
```

- **Docs**: https://developer.atlassian.com/cloud/acli/
- If the binary moves (e.g. to `/usr/local/bin/acli`), update the **Binary path** in the Configuration table above.

## Backup REST Client (use when acli fails)

`acli` can have OAuth session issues. The backup client uses **Basic Auth (email + API token)** which is always stable.

### One-time setup

1. Generate an API token at https://id.atlassian.com/manage/api-tokens
2. Save credentials to `~/.jira-credentials`:
   ```
   JIRA_SITE=paylocity.atlassian.net
   JIRA_EMAIL=aanand@paylocity.com
   JIRA_TOKEN=<your-api-token>
   ```
3. Protect the file: `chmod 600 ~/.jira-credentials`

### Usage

```bash
REST="skills/atlassian-cli/scripts/jira-rest.py"

# Search (outputs JSON array of issue objects, same as acli --json --paginate)
python3 $REST search --jql 'project = BP AND type = "Engineering Escalation"' --paginate

# View a single issue (outputs raw Jira API response, compatible with jira-extract-detail.jq)
python3 $REST view BP-1234

# End-to-end search + detail (drop-in replacement for jira-search-and-detail.sh)
skills/atlassian-cli/scripts/jira-rest-search-and-detail.sh 'project = BP'
```

### When to switch to the backup client

| Symptom                                                         | Cause                                  | Fix                                             |
| --------------------------------------------------------------- | -------------------------------------- | ----------------------------------------------- |
| `failed to search work items`                                   | OAuth token expired or not Jira-scoped | Use backup client                               |
| `failed to fetch work item details`                             | Same OAuth issue                       | Use backup client                               |
| `acli jira auth status` shows `oauth_global` but API calls fail | Global auth doesn't have Jira scope    | Run `acli jira auth login` or use backup client |

## Engineering Escalation Analysis Notes

When producing monthly escalation reports, prefer the existing search-plus-detail utilities instead of hand-built shell loops.

### Recommended flow

```bash
ACLI="/Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli"
JQL='created >= "2026-03-01" AND project = BP AND type = "Engineering Escalation" AND created <= "2026-03-31" ORDER BY key DESC'

skills/atlassian-cli/scripts/jira-search-and-detail.sh "$JQL"
```

If ACLI authentication fails, switch to the REST backup client:

```bash
skills/atlassian-cli/scripts/jira-rest-search-and-detail.sh "$JQL"
```

### Key constraints

- `jira workitem search` only supports the default field set plus `issuetype`; do not request `created`, `reporter`, or `comment` there.
- Use per-issue `view --fields "*all"` or the shared detail scripts when you need comments and metadata.
- `acli jira workitem view` does not populate `.changelog`; infer timelines from created timestamps and comments.
- Jira comment bodies are ADF trees, not plain strings. Extract recursive `.text` content rather than assuming a flat `.body` string.
- Avoid complex inline `jq` inside zsh loops. Prefer the checked-in jq filter files.
- Handle per-key failures defensively so one bad issue does not collapse the whole batch.

### Useful scripts

- `skills/atlassian-cli/scripts/jira-extract-list.jq`
- `skills/atlassian-cli/scripts/jira-extract-detail.jq`
- `skills/atlassian-cli/scripts/jira-bulk-details.sh`
- `skills/atlassian-cli/scripts/jira-search-and-detail.sh`
- `skills/atlassian-cli/scripts/jira-rest.py`
- `skills/atlassian-cli/scripts/jira-rest-bulk-details.sh`
- `skills/atlassian-cli/scripts/jira-rest-search-and-detail.sh`

## Authentication

Before any command, ensure the user is authenticated. Check with:

```bash
$ACLI auth status
```

If not authenticated, guide the user through one of these methods:

| Method              | Use case                          | Command                                                                                         |
| ------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------- |
| OAuth (recommended) | Interactive terminal use          | `$ACLI auth login --web`                                                                        |
| API token           | CI/CD, scripting, non-interactive | `echo <token> \| $ACLI auth login --site "site.atlassian.net" --email "user@email.com" --token` |
| API key             | Admin/org management only         | `$ACLI auth login --api-key <key>`                                                              |

To switch accounts: `$ACLI auth switch`
To logout: `$ACLI auth logout`

## Command Structure

```
acli <PRODUCT> <ENTITY> <ACTION> [FLAGS]
```

- **PRODUCT**: `jira`, `confluence`, `admin`, `rovodev`
- **ENTITY**: `workitem`, `sprint`, `board`, `project`, `page`, `space`, `blog`, `user`
- **ACTION**: `create`, `view`, `edit`, `search`, `delete`, `transition`, `list`, etc.
- **FLAGS**: `--json`, `--csv`, `--jql`, `--key`, `--yes`, etc.

## Procedures

### Jira: Search for Work Items

Use JQL queries to find issues. Always prefer `--json` when parsing output programmatically.

```bash
# Basic search
$ACLI jira workitem search --jql "project = PROJ" --limit 20

# Search with specific fields and CSV output
$ACLI jira workitem search --jql "project = PROJ AND status = 'In Progress'" --fields "key,summary,assignee,status" --csv

# Count results only
$ACLI jira workitem search --jql "assignee = currentUser() AND resolution = Unresolved" --count

# Get all results (paginated)
$ACLI jira workitem search --jql "project = PROJ" --paginate

# JSON output for programmatic use
$ACLI jira workitem search --jql "project = PROJ" --limit 10 --json

# Use a saved filter
$ACLI jira workitem search --filter 10001

# Open results in browser
$ACLI jira workitem search --jql "project = PROJ" --web
```

### Jira: View a Work Item

```bash
# View an issue (default fields: key, type, summary, status, assignee, description)
$ACLI jira workitem view KEY-123

# JSON output
$ACLI jira workitem view KEY-123 --json

# Specific fields only
$ACLI jira workitem view KEY-123 --fields "summary,comment"

# All fields
$ACLI jira workitem view KEY-123 --fields "*all"

# Open in browser
$ACLI jira workitem view KEY-123 --web
```

**Extracting specific data** with jq:

```bash
$ACLI jira workitem view KEY-123 --json | jq '.fields.summary'
```

### Jira: Create a Work Item

Always require `--summary`, `--project`, and `--type` at minimum.

```bash
# Basic creation
$ACLI jira workitem create --summary "Fix login bug" --project "PROJ" --type "Bug"

# With description and assignee
$ACLI jira workitem create --summary "Add dark mode" --project "PROJ" --type "Story" \
  --assignee "user@company.com" --description "Implement dark mode toggle" --label "ui,enhancement"

# Self-assign
$ACLI jira workitem create --summary "Investigate flaky test" --project "PROJ" --type "Task" --assignee "@me"

# Create as child of an epic/parent
$ACLI jira workitem create --summary "Subtask" --project "PROJ" --type "Task" --parent "PROJ-100"

# From a JSON file (useful for complex issues)
$ACLI jira workitem create --from-json "workitem.json"

# Generate a JSON template first
$ACLI jira workitem create --generate-json
```

### Jira: Edit a Work Item

```bash
# Edit summary
$ACLI jira workitem edit --key "KEY-123" --summary "Updated summary"

# Edit multiple issues (confirm before running)
$ACLI jira workitem edit --key "KEY-1,KEY-2,KEY-3" --assignee "user@company.com"

# Bulk edit via JQL — ALWAYS preview count first, then get user approval before adding --yes
$ACLI jira workitem search --jql "project = PROJ AND status = 'To Do'" --count
$ACLI jira workitem edit --jql "project = PROJ AND status = 'To Do'" --assignee "@me" --yes

# Change labels
$ACLI jira workitem edit --key "KEY-123" --labels "bug,critical"

# Remove assignee
$ACLI jira workitem edit --key "KEY-123" --remove-assignee
```

### Jira: Qase Automation Tracking Ticket Pattern

Use this pattern when opening Jira work to automate an existing Qase test case.

```bash
$ACLI jira workitem create \
   --project "BP" \
   --type "Task" \
   --summary "Automate Qase test ABP-7: <test case title>" \
   --description "Qase Test Case: ABP-7 (https://app.qase.io/case/ABP-7)

Title: <test case title>

Current Status: Manual test

Acceptance Criteria:
- Create the automation that covers the Qase scenario
- Link the automation back to Qase with the qase(...) wrapper
- Update the Qase case status after the automation is merged" \
   --parent "BP-7479"

$ACLI jira workitem edit --key "BP-1234" --labels "bp-velocity"
```

Notes:

- If the issue should be unassigned, omit `--assignee`.
- Apply labels after creation if they are not part of the create flow.
- Reuse the exact Qase case ID and link in the description for traceability.

### Jira: Transition a Work Item

Move issues between workflow statuses.

```bash
# Single issue
$ACLI jira workitem transition --key "KEY-123" --status "In Progress"

# Multiple issues
$ACLI jira workitem transition --key "KEY-1,KEY-2" --status "Done"

# Bulk transition via JQL — ALWAYS preview count first, then get user approval before adding --yes
$ACLI jira workitem search --jql "project = PROJ AND assignee = currentUser()" --count
$ACLI jira workitem transition --jql "project = PROJ AND assignee = currentUser()" --status "Done" --yes
```

### Jira: Comments

```bash
# Add a comment
$ACLI jira workitem comment create --key "KEY-123" --body "Working on this now"

# Add from file
$ACLI jira workitem comment create --key "KEY-123" --body-file "comment.txt"

# List comments
$ACLI jira workitem comment list --key "KEY-123"

# Edit last comment by current user
$ACLI jira workitem comment create --key "KEY-123" --body "Updated comment" --edit-last
```

### Jira: Sprints

```bash
# List sprints for a board
$ACLI jira board list-sprints --board 1

# View sprint details
$ACLI jira sprint view --sprint 42 --board 1

# List work items in a sprint
$ACLI jira sprint list-workitems --sprint 42 --board 1

# Create a sprint
$ACLI jira sprint create --board 1 --name "Sprint 15"
```

### Jira: Projects and Boards

```bash
# List all projects
$ACLI jira project list

# View a project
$ACLI jira project view --key "PROJ"

# Search boards
$ACLI jira board search --name "Team"
```

### Confluence: Pages

```bash
# View a page by ID
$ACLI confluence page view --id 123456789

# View in JSON
$ACLI confluence page view --id 123456789 --json

# View with specific body format (storage, atlas_doc_format, view)
$ACLI confluence page view --id 123456789 --body-format storage

# Include child pages
$ACLI confluence page view --id 123456789 --include-direct-children
```

### Confluence: Spaces

```bash
# List all spaces
$ACLI confluence space list

# View a space
$ACLI confluence space view --key "TEAM"

# Create a space
$ACLI confluence space create --key "NEWSPACE" --name "New Space"
```

### Confluence: Blog Posts

```bash
# List blog posts
$ACLI confluence blog list --space "TEAM"

# Create a blog post
$ACLI confluence blog create --space "TEAM" --title "Release Notes" --body "Content here"

# View a blog post
$ACLI confluence blog view --id 987654321
```

## Output Formats

| Flag      | Format  | Best for                     |
| --------- | ------- | ---------------------------- |
| (default) | Table   | Human reading                |
| `--json`  | JSON    | Programmatic parsing with jq |
| `--csv`   | CSV     | Spreadsheets, data export    |
| `--web`   | Browser | Quick visual inspection      |

## Chaining and Piping

```bash
# Chain: search then confirm
$ACLI jira workitem search --jql 'project = PROJ' --limit 10 && echo "Done"

# Redirect to file
$ACLI jira workitem search --jql 'project = PROJ' --csv > issues.csv

# Pipe to grep
$ACLI jira workitem search --jql 'project = PROJ' --limit 50 | grep "To Do"

# Pipe JSON to jq
$ACLI jira workitem view KEY-123 --json | jq '.fields.summary'
```

## Common JQL Patterns

Reference for building JQL queries:

| Intent            | JQL                                                    |
| ----------------- | ------------------------------------------------------ |
| My open issues    | `assignee = currentUser() AND resolution = Unresolved` |
| Project bugs      | `project = PROJ AND issuetype = Bug`                   |
| High priority     | `project = PROJ AND priority in (High, Highest)`       |
| Created this week | `project = PROJ AND created >= startOfWeek()`          |
| Updated recently  | `project = PROJ AND updated >= -7d`                    |
| Unassigned        | `project = PROJ AND assignee is EMPTY`                 |
| Specific sprint   | `sprint = "Sprint 15"`                                 |
| Epics             | `project = PROJ AND issuetype = Epic`                  |
| Text search       | `project = PROJ AND text ~ "login bug"`                |

## Guardrails

### Risk Classification

Every acli command falls into one of three tiers. **Follow the required behavior strictly.**

| Tier          | Risk                                            | Required behavior                                                                        |
| ------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------- |
| **Safe**      | None — read-only                                | Run freely, no confirmation needed                                                       |
| **Moderate**  | Creates or modifies a single item               | Show the user what will be done and **ask for confirmation** before executing            |
| **Dangerous** | Bulk mutation, deletion, or irreversible action | **MUST get explicit user approval**. Preview the blast radius first. Never auto-confirm. |

### Safe operations (run freely)

- `workitem view`, `workitem search`, `workitem comment list`
- `project list`, `project view`
- `board search`, `board get`, `board list-projects`, `board list-sprints`
- `sprint view`, `sprint list-workitems`
- `confluence page view`, `confluence space list`, `confluence space view`
- `confluence blog list`, `confluence blog view`
- `auth status`
- Any command with `--help`
- Any command with `--count` (just counting, no mutation)

### Moderate operations (confirm before executing)

Before running, tell the user exactly what will happen and wait for approval:

- `workitem create` — show summary, project, type, assignee
- `workitem edit --key "SINGLE-KEY"` — show which fields are changing
- `workitem transition --key "SINGLE-KEY"` — show issue key and target status
- `workitem comment create` — show key and comment body
- `workitem assign` — show key and new assignee
- `sprint create`, `sprint update`
- `confluence space create`, `confluence blog create`

### Dangerous operations (MUST get explicit user approval)

**NEVER run these without the user explicitly saying "yes" or "go ahead":**

1. **Bulk edit/transition via JQL or filter**:
   - Before proposing: run `workitem search --jql "<same JQL>" --count` and show the count
   - Tell the user: "This will modify **N** work items. Proceed?"
   - Do NOT pass `--yes` until the user confirms

   ```bash
   # Step 1: Preview count
   $ACLI jira workitem search --jql "project = PROJ AND status = 'To Do'" --count
   # Step 2: Only after user confirms
   $ACLI jira workitem edit --jql "project = PROJ AND status = 'To Do'" --assignee "@me" --yes
   ```

2. **Delete operations** (`workitem delete`, `sprint delete`, `board delete`, `project delete`):
   - Always suggest `archive` instead if available
   - If the user insists on delete, show exactly what will be deleted
   - For `project delete`: warn that **all issues in the project will be lost**
   - Never pass `--yes` until the user explicitly confirms

3. **Bulk delete via JQL**: Same as bulk edit — preview count first, get approval, then execute

4. **Auth operations** (`auth logout`, `auth switch`):
   - Warn the user that switching/logging out affects all subsequent commands
   - Confirm before executing

### Mandatory Pre-flight Checks

**Before any JQL-based mutation** (edit, transition, delete with `--jql` or `--filter`):

1. Run the same query as `workitem search --count` first
2. Show the count to the user
3. If count > 10, also show a sample: `workitem search --jql "..." --limit 5 --fields "key,summary,status"`
4. Wait for explicit confirmation before proceeding

**Never pass `--yes` automatically.** The `--yes` flag skips acli's built-in confirmation prompt. Only add it after the user has already confirmed through the chat.

### Additional Safety Rules

- **Archive over delete**: Always prefer `archive` commands over `delete` when both are available
- **Sensitive data**: Never log or display API tokens. When authenticating with `--token`, always pipe from stdin or file, never pass as a command-line argument
- **Test JQL first**: Always validate a JQL query with `workitem search` before using it in any mutating command
- **One-at-a-time for unfamiliar workflows**: If unsure about the effect of a command, run it on a single issue first before applying to multiple

## Common Workflows

> **Customize these** with your actual project key, board ID, and team conventions.

### Morning Standup: What's on my plate?

```bash
# My open issues, ordered by priority
$ACLI jira workitem search --jql "assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC" --fields "key,summary,status,priority" --limit 20

# What I updated yesterday
$ACLI jira workitem search --jql "assignee = currentUser() AND updated >= -1d" --fields "key,summary,status"
```

### Sprint Planning: Current sprint overview

```bash
# List work items in the active sprint (update board/sprint IDs)
$ACLI jira sprint list-workitems --sprint <SPRINT_ID> --board <BOARD_ID>

# Unassigned items in the sprint
$ACLI jira workitem search --jql "sprint = <SPRINT_ID> AND assignee is EMPTY" --fields "key,summary,priority"
```

### Quick Triage: Create and assign a bug

```bash
$ACLI jira workitem create --summary "Describe the bug" --project "MYPROJECT" --type "Bug" --assignee "@me" --label "triage"
```

### End of Day: Close out finished work

```bash
# First: preview what will be transitioned
$ACLI jira workitem search --jql "assignee = currentUser() AND status = 'In Review' AND project = MYPROJECT" --count
# Then after user confirms:
$ACLI jira workitem transition --jql "assignee = currentUser() AND status = 'In Review' AND project = MYPROJECT" --status "Done" --yes
```

### Export: Get issues as CSV for a report

```bash
$ACLI jira workitem search --jql "project = MYPROJECT AND created >= startOfWeek()" --fields "key,summary,assignee,status,priority,created" --csv > weekly_issues.csv
```

## Troubleshooting

- **Not authenticated**: Run `$ACLI auth status` to check. Re-authenticate with `$ACLI jira auth login --web`.
- **Permission denied**: The authenticated user may not have access to the project or action. Check Jira permissions.
- **Unknown command**: Run `$ACLI <command> --help` to discover available subcommands and flags.
- **JQL syntax error**: Validate JQL in Jira's web UI issue search first, then copy to CLI.
- **For full docs**: https://developer.atlassian.com/cloud/acli/
