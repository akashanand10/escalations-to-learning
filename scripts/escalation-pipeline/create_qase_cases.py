#!/usr/bin/env python3
"""Bulk-create Qase test cases for an escalation coverage review (Phase 4).

Reads a JSON config of approved cases (one entry per case) and creates each in
Qase via `.agents/skills/qase-api/scripts/qase-rest.py create-case`. Performs a
local fuzzy duplicate check against an existing-cases JSON dump (Jaccard >= 0.80
on lowercased word tokens of length > 3); duplicates are skipped, not created.

Inputs
------
--config PATH       JSON file. Schema:
                      {
                        "project": "ABP",
                        "existing_cases_json": "/path/to/abp_cases.json",
                        "defaults": {
                          "severity": 2, "priority": 1, "type": 3,
                          "custom_field_id": 142,
                          "custom_field_value": "AI escalation context"
                        },
                        "cases": [
                          {"jira": "BP-7828", "suite_id": 35, "title": "Verify ..."},
                          ...
                        ]
                      }
--output PATH       Where to write the per-case results JSON
                    (default: ./qase_create_results.json)
--dry-run           Print what would be created, do not call Qase

Output JSON entry
-----------------
{ "idx": N, "jira": "BP-...", "title": "...",
  "status": "created" | "skipped" | "failed",
  "id": <int>          # when created
  "dup_id": <int>, "dup_title": "..."  # when skipped
  "error": "..."       # when failed
}
"""
from __future__ import annotations
import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
QASE_SCRIPT = REPO_ROOT / ".agents" / "skills" / "qase-api" / "scripts" / "qase-rest.py"


def normalize(s: str) -> set[str]:
    s = s.lower()
    s = re.sub(r"[^\w\s]", " ", s)
    return {w for w in s.split() if len(w) > 3}


def find_dup(title: str, existing: list[dict], threshold: float = 0.80):
    new_tokens = normalize(title)
    if not new_tokens:
        return None
    best = (0.0, None)
    for c in existing:
        ex_tokens = normalize(c.get("title", ""))
        if not ex_tokens:
            continue
        jac = len(new_tokens & ex_tokens) / len(new_tokens | ex_tokens)
        if jac > best[0]:
            best = (jac, c)
    return best[1] if best[0] >= threshold else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", required=True, type=Path)
    ap.add_argument("--output", default=Path("qase_create_results.json"), type=Path)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text())
    project = cfg["project"]
    existing = json.loads(Path(cfg["existing_cases_json"]).read_text())
    d = cfg.get("defaults", {})
    severity = str(d.get("severity", 2))
    priority = str(d.get("priority", 1))
    case_type = str(d.get("type", 3))
    cf_id = d.get("custom_field_id", 142)
    cf_val = d.get("custom_field_value", "AI escalation context")
    cases = cfg["cases"]

    results: list[dict] = []
    for i, case in enumerate(cases, 1):
        jira = case["jira"]
        suite_id = int(case["suite_id"])
        title = case["title"]
        print(f"\n[{i}/{len(cases)}] {jira} | suite {suite_id} | {title[:90]}")

        dup = find_dup(title, existing)
        if dup:
            print(f"  DUPLICATE: ABP-{dup['id']} ({dup['title'][:80]}) — skipping")
            results.append({
                "idx": i, "jira": jira, "title": title, "status": "skipped",
                "dup_id": dup["id"], "dup_title": dup["title"],
            })
            continue

        if args.dry_run:
            print("  DRY-RUN — would create")
            results.append({"idx": i, "jira": jira, "title": title, "status": "dry-run"})
            continue

        desc = (
            f'<p><strong>Source escalation:</strong> '
            f'<a href="https://paylocity.atlassian.net/browse/{jira}">{jira}</a></p>'
            f'<p>Created from escalation test coverage review.</p>'
        )
        cmd = [
            "python3", str(QASE_SCRIPT), "create-case",
            "--project", project,
            "--title", title,
            "--suite-id", str(suite_id),
            "--severity", severity,
            "--priority", priority,
            "--type", case_type,
            "--description", desc,
            "--custom-field", f"{cf_id}={cf_val}",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            print(f"  FAILED rc={proc.returncode}: {proc.stderr.strip()[:200]}")
            results.append({
                "idx": i, "jira": jira, "title": title, "status": "failed",
                "error": proc.stderr.strip()[:300],
            })
            continue
        cid = None
        try:
            out = json.loads(proc.stdout)
            cid = out.get("id") or out.get("result", {}).get("id")
        except Exception:
            m = re.search(r'"id":\s*(\d+)', proc.stdout)
            if m:
                cid = int(m.group(1))
        print(f"  CREATED {project}-{cid}")
        results.append({"idx": i, "jira": jira, "title": title, "status": "created", "id": cid})
        time.sleep(0.2)

    args.output.write_text(json.dumps(results, indent=2))
    created = sum(1 for r in results if r["status"] == "created")
    skipped = sum(1 for r in results if r["status"] == "skipped")
    failed = sum(1 for r in results if r["status"] == "failed")
    print(f"\n=== SUMMARY ===")
    print(f"Created: {created}")
    print(f"Skipped (duplicates): {skipped}")
    print(f"Failed: {failed}")
    print(f"Results written to: {args.output}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
