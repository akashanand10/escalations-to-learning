# jira-extract-list.jq
# Usage: $ACLI jira workitem search --jql "..." --paginate --json | jq -f jira-extract-list.jq
#
# Extracts a compact array of {key, summary, priority, status, owner, customer}
# from the paginated search JSON output. Customer name is parsed from "[Customer] ..." summary prefix.

[
  .[] | {
    key,
    summary: .fields.summary,
    priority: (.fields.priority.name // "Unknown"),
    status: (.fields.status.name // "Unknown"),
    owner: (.fields.assignee.displayName // "Unassigned"),
    customer: (
      try (.fields.summary | capture("^\\[(?<c>[^\\]]+)\\]").c)
      catch "Not specified"
    )
  }
]
