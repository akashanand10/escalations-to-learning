#!/usr/bin/env python3
"""Bulk-create Jira automation tasks for created Qase cases (Phase 5).

Reads the JSON output from `create_qase_cases.py` (entries with status=created)
and creates one Jira `Task` per Qase case under a configurable parent issue,
distributing assignees round-robin across a list of accountIds.

Inputs
------
--qase-results PATH      JSON produced by create_qase_cases.py
--config PATH            JSON file. Schema:
                           {
                             "project": "BP",
                             "issuetype": "Task",
                             "parent": "BP-7479",
                             "label": "bp-velocity",
                             "qase_project": "ABP",
                             "assignees": [
                               {"name": "Akash Anand",      "account_id": "712020:..."},
                               {"name": "Sachin Mannurkar", "account_id": "712020:..."}
                             ]
                           }
--output PATH            Where to write per-task results JSON
                         (default: ./jira_automation_results.json)
--dry-run                Print what would be created, do not call Jira

Distribution
------------
Cases are assigned round-robin in input order across `assignees`. With 2
assignees and 36 cases that yields 18/18.
"""
from __future__ import annotations
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
JIRA_SCRIPT = REPO_ROOT / ".agents" / "skills" / "jira-rest-api" / "scripts" / "jira-rest-client.py"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--qase-results", required=True, type=Path)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--output", default=Path("jira_automation_results.json"), type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    project = cfg["project"]
    issuetype = cfg.get("issuetype", "Task")
    parent = cfg["parent"]
    label = cfg.get("label")
    qase_project = cfg.get("qase_project", "ABP")
    assignees = cfg["assignees"]
    if not assignees:
        print("ERROR: at least one assignee required", file=sys.stderr)
        return 2

    qase_results = json.loads(args.qase_results.read_text())
    created_cases = [r for r in qase_results if r.get("status") == "created"]

    out: list[dict] = []
    for i, c in enumerate(created_cases):
        a = assignees[i % len(assignees)]
        qase_id = f"{qase_project}-{c['id']}"
        title = c["title"]
        summary = f"Automate Qase test {qase_id}: {title}"
        description = (
            f"Automate the following Qase test case:\n\n"
            f"Qase: https://app.qase.io/case/{qase_id}\n"
            f"Source escalation: https://paylocity.atlassian.net/browse/{c['jira']}\n\n"
            f"Acceptance Criteria:\n"
            f"- Create Playwright automation for this test case\n"
            f"- Link with qase('{qase_id}') wrapper\n"
            f"- Update Qase automation status after merge"
        )

        print(f"\n[{i + 1}/{len(created_cases)}] Creating: {summary[:90]}")

        fields: dict = {
            "project": {"key": project},
            "issuetype": {"name": issuetype},
            "summary": summary,
            "parent": {"key": parent},
            "assignee": {"accountId": a["account_id"]},
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": description}]}
                ],
            },
        }
        if label:
            fields["labels"] = [label]

        if args.dry_run:
            print(f"  DRY-RUN — would assign to {a['name']}")
            out.append({
                "qase_id": qase_id, "jira_src": c["jira"], "status": "dry-run",
                "assignee_name": a["name"], "assignee_id": a["account_id"],
            })
            continue

        proc = subprocess.run(
            ["python3", str(JIRA_SCRIPT), "create", "--json-payload", json.dumps({"fields": fields})],
            capture_output=True, text=True,
        )
        if proc.returncode != 0:
            print(f"  FAILED rc={proc.returncode}: {proc.stderr.strip()[:300]}")
            out.append({
                "qase_id": qase_id, "jira_src": c["jira"], "status": "failed",
                "assignee_name": a["name"], "assignee_id": a["account_id"],
                "error": proc.stderr.strip()[:400],
            })
            continue
        issue_key = None
        try:
            data = json.loads(proc.stdout)
            issue_key = data.get("key")
        except Exception:
            pass
        print(f"  CREATED {issue_key} (assignee: {a['name']})")
        out.append({
            "qase_id": qase_id, "jira_src": c["jira"], "status": "created",
            "issue_key": issue_key,
            "assignee_id": a["account_id"], "assignee_name": a["name"],
        })
        time.sleep(0.2)

    args.output.write_text(json.dumps(out, indent=2))
    ok = [r for r in out if r["status"] == "created"]
    fail = [r for r in out if r["status"] == "failed"]
    print(f"\n=== SUMMARY ===")
    print(f"Created: {len(ok)}")
    for a in assignees:
        n = sum(1 for r in ok if r.get("assignee_id") == a["account_id"])
        print(f"  {a['name']}: {n}")
    print(f"Failed: {len(fail)}")
    print(f"Results written to: {args.output}")
    return 0 if not fail else 1


if __name__ == "__main__":
    sys.exit(main())
