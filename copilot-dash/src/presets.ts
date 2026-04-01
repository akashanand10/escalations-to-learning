export interface PresetQuery {
  id: string;
  label: string;
  category: "escalation" | "qase" | "jira" | "analysis" | "custom";
  prompt: string;
  effort?: "low" | "medium" | "high" | "xhigh";
  tools?: boolean;
  description?: string;
  custom?: boolean;
}

export const PRESETS: PresetQuery[] = [
  // ─── Escalation Analysis ───────────────────────────────────────
  {
    id: "esc-march-summary",
    label: "March 2026 Escalation Summary",
    category: "escalation",
    prompt:
      "Read the file analysis/bp-engineering-escalations-march-2026-analysis.md and provide a concise summary: total tickets, top product areas, most critical issues, and any recurring themes.",
    effort: "high",
    tools: true,
    description: "Summarize the March 2026 escalation analysis report",
  },
  {
    id: "esc-feb-summary",
    label: "February 2026 Escalation Summary",
    category: "escalation",
    prompt:
      "Read the file analysis/bp-engineering-escalations-february-2026-analysis.md and provide a concise summary: total tickets, top product areas, most critical issues, and any recurring themes.",
    effort: "high",
    tools: true,
    description: "Summarize the February 2026 escalation analysis report",
  },
  {
    id: "esc-trend-compare",
    label: "Feb vs March Trend Comparison",
    category: "escalation",
    prompt:
      "Read analysis/bp-engineering-escalations-february-2026-analysis.md and analysis/bp-engineering-escalations-march-2026-analysis.md. Compare the two months: which product areas improved, which got worse, any new categories, and overall ticket volume trend.",
    effort: "high",
    tools: true,
    description: "Compare escalation trends between February and March 2026",
  },
  {
    id: "esc-hotspots",
    label: "Identify Escalation Hotspots",
    category: "escalation",
    prompt:
      "Read all files in the analysis/ directory. Identify the top 5 product area hotspots with the most recurring escalations. For each hotspot, list the specific tickets and suggest preventive actions.",
    effort: "high",
    tools: true,
    description: "Find the most problematic product areas across all months",
  },
  {
    id: "esc-open-tickets",
    label: "List Open/In-Progress Tickets",
    category: "escalation",
    prompt:
      "Read all files in the analysis/ directory. List all tickets that are still open or in-progress (not resolved/closed). Include the ticket key, summary, owner, and current status.",
    effort: "medium",
    tools: true,
    description: "Find all unresolved escalation tickets",
  },

  // ─── Qase Test Management ─────────────────────────────────────
  {
    id: "qase-automation-stats",
    label: "Qase Automation Coverage Stats",
    category: "qase",
    prompt:
      "Run this command and summarize the output: python3 ~/.agents/skills/qase-api/scripts/qase-rest.py list-cases --project ABP --paginate | python3 -c \"import sys,json; data=json.load(sys.stdin); total=len(data); auto=sum(1 for c in data if not c.get('isManual',True)); manual=sum(1 for c in data if c.get('isManual',True)); print(f'Total: {total}, Automated: {auto} ({auto*100//total}%), Manual: {manual} ({manual*100//total}%)')\"",
    tools: true,
    description: "Get automation vs manual test case counts for ABP",
  },
  {
    id: "qase-failed-runs",
    label: "Recent Failed Test Runs",
    category: "qase",
    prompt:
      "Run: python3 ~/.agents/skills/qase-api/scripts/qase-rest.py list-runs --project ABP --status failed --paginate. Summarize the results: how many failed runs, their titles, and dates.",
    tools: true,
    description: "List recently failed test runs in the ABP project",
  },
  {
    id: "qase-coverage-gaps",
    label: "Test Coverage Gap Analysis",
    category: "qase",
    prompt:
      "Read the escalation analysis files in analysis/ to identify the key issue areas. Then run: python3 ~/.agents/skills/qase-api/scripts/qase-rest.py list-cases --project ABP --paginate. Cross-reference to find which escalation areas lack test coverage.",
    effort: "high",
    tools: true,
    description: "Find gaps between escalation issues and Qase test coverage",
  },
  {
    id: "qase-list-suites",
    label: "List All Test Suites",
    category: "qase",
    prompt:
      "Run: python3 ~/.agents/skills/qase-api/scripts/qase-rest.py list-suites --project ABP --paginate. Present the suites in a clean hierarchy showing parent-child relationships and case counts.",
    tools: true,
    description: "Show the ABP test suite hierarchy",
  },

  // ─── Jira Queries ─────────────────────────────────────────────
  {
    id: "jira-recent-escalations",
    label: "Recent Jira Escalations (This Month)",
    category: "jira",
    prompt:
      'Run: /Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli jira workitem search --jql \'created >= "2026-03-01" AND project = BP AND type = "Engineering Escalation" AND created <= "2026-03-31" ORDER BY key DESC\' --paginate --json | jq \'[.[] | {key, summary: .fields.summary, status: .fields.status.name, priority: .fields.priority.name, created: .fields.created}]\'. Summarize the results.',
    tools: true,
    description: "Search Jira for March 2026 engineering escalations",
  },
  {
    id: "jira-high-priority",
    label: "High Priority Open Escalations",
    category: "jira",
    prompt:
      "Run: /Users/aanand/Downloads/acli_0.1.2_darwin_arm64/acli jira workitem search --jql 'project = BP AND type = \"Engineering Escalation\" AND priority in (Highest, High) AND status not in (Done, Closed, Resolved) ORDER BY priority DESC, created DESC' --paginate --json | jq '[.[] | {key, summary: .fields.summary, status: .fields.status.name, priority: .fields.priority.name}]'. List and summarize.",
    tools: true,
    description: "Find high-priority unresolved engineering escalations",
  },

  // ─── General Analysis ─────────────────────────────────────────
  {
    id: "analysis-quarterly",
    label: "Generate Quarterly Report Outline",
    category: "analysis",
    prompt:
      "Read the quarterly-escalation-analysis.instructions.md file and the analysis/ directory files. Based on the instructions and available data, generate an outline for the Q1 2026 quarterly escalation report with key sections and data points to include.",
    effort: "high",
    tools: true,
    description: "Draft a quarterly report outline from available monthly data",
  },
  {
    id: "analysis-action-items",
    label: "Extract All Action Items",
    category: "analysis",
    prompt:
      "Read all files in analysis/. Extract every action item, next step, or follow-up mentioned across all tickets. Group them by owner/assignee if possible, otherwise by product area.",
    effort: "medium",
    tools: true,
    description: "Pull all pending action items from escalation reports",
  },
];
