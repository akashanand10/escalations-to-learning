# jira-extract-detail.jq
# Usage: $ACLI jira workitem view KEY-123 --fields "*all" --json | jq -f jira-extract-detail.jq
#
# Extracts a structured object from a single workitem view (--fields "*all") including:
# key, summary, created, reporter, priority, status, owner, customer, and all comments.
#
# Comments are returned as an array sorted chronologically with author, date, and body text.

def extract_text:
  [.. | objects | .text? // empty] | join(" ") | gsub("\\s+"; " ") | .[0:300];

{
  key,
  summary: .fields.summary,
  created: (.fields.created // null),
  reporter: (.fields.reporter.displayName // "Unknown"),
  priority: (.fields.priority.name // "Unknown"),
  status: (.fields.status.name // "Unknown"),
  owner: (.fields.assignee.displayName // "Unassigned"),
  customer: (
    first((.fields.summary | capture("^\\[(?<c>[^\\]]+)\\]").c), "Not specified")
  ),
  comments: (
    (.fields.comment.comments // [])
    | sort_by(.created)
    | map({
        author: (.author.displayName // "Unknown"),
        date: (.created | split("T")[0]),
        body: (.body | extract_text)
      })
  )
}
