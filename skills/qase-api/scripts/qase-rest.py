#!/usr/bin/env python3
"""
qase-rest.py — Qase REST API v1 client using API token authentication.

SETUP
  Store credentials (first match wins):
    1. Env var:  QASE_API_TOKEN=<token>
    2. File:     ~/.qase-credentials   (QASE_API_TOKEN=<token>)
  Generate token: https://app.qase.io/user/api/token
  Protect creds:  chmod 600 ~/.qase-credentials

READ COMMANDS  (safe — run freely)
  list-projects                                               [--paginate] [--limit N]
  get-project       --project CODE
  list-suites       --project CODE                           [--paginate] [--limit N]
  get-suite         --project CODE <id>
  list-cases        --project CODE  [--suite-id N] [--search TEXT]
                                    [--status actual|draft|deprecated]
                                    [--milestone-id N]
                                    [--severity undefined|blocker|critical|major|normal|minor|trivial]
                                    [--priority undefined|high|medium|low]
                                    [--type other|functional|smoke|regression|security|usability|performance|acceptance]
                                    [--behavior undefined|positive|negative|destructive]
                                    [--automation is-not-automated|automated]
                                                             [--paginate] [--limit N]
  get-case          --project CODE <id>
  list-runs         --project CODE  [--status in_progress|passed|failed|aborted]
                                                             [--paginate] [--limit N]
  get-run           --project CODE <id>  [--include cases,defects]
  list-results      --project CODE  [--run N] [--case-id N]
                                    [--status passed|failed|blocked|skipped|invalid]
                                    [--from-time "YYYY-MM-DD HH:MM:SS"]
                                    [--to-time   "YYYY-MM-DD HH:MM:SS"]
                                                             [--paginate] [--limit N]
  get-result        --project CODE <hash>
  list-defects      --project CODE  [--status STATUS]        [--paginate] [--limit N]
  get-defect        --project CODE <id>
  list-milestones   --project CODE                           [--paginate] [--limit N]
  list-plans        --project CODE                           [--paginate] [--limit N]
  get-plan          --project CODE <id>
  list-environments --project CODE                           [--paginate] [--limit N]
  list-custom-fields                                         [--paginate] [--limit N]
  list-shared-steps --project CODE                           [--paginate] [--limit N]
  list-attachments                                           [--paginate] [--limit N]
  get-attachment    <hash>
  list-users                                                 [--paginate] [--limit N]
  list-authors                                               [--paginate] [--limit N]
  get-system-fields
  search            --query "QQL expression"                 [--paginate] [--limit N]

WRITE COMMANDS  (confirm with user before running)
  create-run        --project CODE --title TEXT
                    [--cases 1,2,3] [--include-all] [--plan-id N]
                    [--env-id N] [--milestone-id N] [--description TEXT]
  complete-run      --project CODE <id>
  create-result     --project CODE --run N --case-id N
                    --status passed|failed|blocked|skipped|invalid
                    [--time-ms N] [--comment TEXT] [--stacktrace TEXT] [--defect]
  bulk-results      --project CODE --run N --data JSON|@filepath
  create-case       --project CODE --title TEXT
                    [--suite-id N] [--milestone-id N]
                    [--severity N] [--priority N] [--type N]
                    [--behavior N] [--automation N] [--status N] [--layer N]
                    [--is-flaky N] [--steps-type classic|gherkin]
                    [--description TEXT] [--preconditions TEXT]
                    [--postconditions TEXT] [--tags tag1,tag2]
  update-case       --project CODE <id>
                    [--title TEXT] [--suite-id N] [--milestone-id N]
                    [--severity N] [--priority N] [--type N]
                    [--behavior N] [--automation N] [--status N] [--layer N]
                    [--is-flaky N] [--steps-type classic|gherkin]
                    [--description TEXT] [--preconditions TEXT]
                    [--postconditions TEXT] [--tags tag1,tag2]
  bulk-cases        --project CODE --data JSON|@filepath
  attach-external-issue --project CODE --type jira-cloud|jira-server --links JSON|@filepath
  create-defect     --project CODE --title TEXT
                    [--severity N] [--actual-result TEXT]
  resolve-defect    --project CODE <id>

DESTRUCTIVE COMMANDS  (MUST get explicit user approval before running)
  delete-case       --project CODE <id>
  delete-run        --project CODE <id>
  delete-result     --project CODE <hash>
  delete-defect     --project CODE <id>

OUTPUT
  list-*       → JSON array  [{...}, ...]  — pipe to jq
  get-*        → JSON object
  create-*     → JSON object (the created entity)
  Other writes → {"status": true|false}

FIELD VALUE REFERENCE
  Case severity:   0=undefined 1=blocker 2=critical 3=major 4=normal 5=minor 6=trivial
  Case priority:   0=undefined 1=high 2=medium 3=low
  Case type:       0=other 1=functional 2=smoke 3=regression 4=security
                   5=usability 6=performance 7=acceptance
  Case behavior:   0=undefined 1=positive 2=negative 3=destructive
  Case automation (new fields on entity):
    isManual (bool):        true=manual, false=automated
    isToBeAutomated (bool): checkbox, independent of isManual
    automation (int, legacy): 0=manual 2=automated
  Case status:     0=actual 1=draft 2=deprecated
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error

CREDENTIALS_FILE = os.path.expanduser("~/.qase-credentials")
BASE_URL = "https://api.qase.io/v1"


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def load_credentials():
    token = os.environ.get("QASE_API_TOKEN")

    if not token and os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                if key.strip() == "QASE_API_TOKEN" and value.strip():
                    token = value.strip()
                    break

    if not token:
        print("Error: Missing QASE_API_TOKEN", file=sys.stderr)
        print(f"Set it as an env var or add to {CREDENTIALS_FILE}:", file=sys.stderr)
        print("  QASE_API_TOKEN=<token from https://app.qase.io/user/api/token>", file=sys.stderr)
        sys.exit(1)

    return token


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _request(method, url, token, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Token": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f"HTTP {e.code} {e.reason}: {body_text}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def api_get(token, path, params=None):
    url = f"{BASE_URL}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    return _request("GET", url, token)


def api_post(token, path, data=None):
    url = f"{BASE_URL}/{path}"
    return _request("POST", url, token, data if data is not None else {})


def api_patch(token, path, data=None):
    url = f"{BASE_URL}/{path}"
    return _request("PATCH", url, token, data if data is not None else {})


def api_delete(token, path):
    url = f"{BASE_URL}/{path}"
    return _request("DELETE", url, token)


def load_json_arg(value):
    """Parse a JSON argument: raw JSON string or @filepath."""
    if value.startswith("@"):
        with open(value[1:]) as f:
            return json.load(f)
    return json.loads(value)


# ---------------------------------------------------------------------------
# Pagination helper
# ---------------------------------------------------------------------------

def paginate_list(token, path, params, limit, do_paginate):
    """Fetch one or all pages from a Qase list endpoint."""
    all_entities = []
    offset = 0
    params = dict(params)
    params["limit"] = min(limit, 100)

    while True:
        params["offset"] = offset
        result = api_get(token, path, params)
        entities = result.get("result", {}).get("entities", [])
        all_entities.extend(entities)
        total = result.get("result", {}).get("total", result.get("result", {}).get("count", 0))

        if not do_paginate or not entities or offset + len(entities) >= total:
            break

        offset += len(entities)

    return all_entities


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

# --- READ: Projects ---

def cmd_list_projects(args, token):
    entities = paginate_list(token, "project", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_project(args, token):
    result = api_get(token, f"project/{args.project}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Suites ---

def cmd_list_suites(args, token):
    entities = paginate_list(token, f"suite/{args.project}", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_suite(args, token):
    result = api_get(token, f"suite/{args.project}/{args.id}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Test Cases ---

def cmd_list_cases(args, token):
    params = {}
    if args.suite_id:
        params["suite_id"] = args.suite_id
    if args.search:
        params["search"] = args.search
    if args.status:
        params["status"] = args.status
    if args.milestone_id:
        params["milestone_id"] = args.milestone_id
    if args.severity:
        params["severity"] = args.severity
    if args.priority:
        params["priority"] = args.priority
    if args.type:
        params["type"] = args.type
    if args.behavior:
        params["behavior"] = args.behavior
    if args.automation:
        params["automation"] = args.automation
    entities = paginate_list(token, f"case/{args.project}", params, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_case(args, token):
    result = api_get(token, f"case/{args.project}/{args.id}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Test Runs ---

def cmd_list_runs(args, token):
    params = {}
    if args.status:
        params["status"] = args.status
    entities = paginate_list(token, f"run/{args.project}", params, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_run(args, token):
    params = {}
    if args.include:
        params["include"] = args.include
    result = api_get(token, f"run/{args.project}/{args.id}", params or None)
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Results ---

def cmd_list_results(args, token):
    params = {}
    if args.run:
        params["run"] = args.run
    if args.case_id:
        params["case_id"] = args.case_id
    if args.status:
        params["status"] = args.status
    if args.from_time:
        params["from_end_time"] = args.from_time
    if args.to_time:
        params["to_end_time"] = args.to_time
    entities = paginate_list(token, f"result/{args.project}", params, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_result(args, token):
    result = api_get(token, f"result/{args.project}/{args.hash}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Defects ---

def cmd_list_defects(args, token):
    params = {}
    if args.status:
        params["status"] = args.status
    entities = paginate_list(token, f"defect/{args.project}", params, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_defect(args, token):
    result = api_get(token, f"defect/{args.project}/{args.id}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Milestones, Plans, Environments ---

def cmd_list_milestones(args, token):
    entities = paginate_list(token, f"milestone/{args.project}", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_list_plans(args, token):
    entities = paginate_list(token, f"plan/{args.project}", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_plan(args, token):
    result = api_get(token, f"plan/{args.project}/{args.id}")
    print(json.dumps(result.get("result", result), indent=2))


def cmd_list_environments(args, token):
    entities = paginate_list(token, f"environment/{args.project}", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


# --- READ: Custom Fields, Shared Steps, Attachments ---

def cmd_list_custom_fields(args, token):
    entities = paginate_list(token, "custom_field", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_list_shared_steps(args, token):
    entities = paginate_list(token, f"shared_step/{args.project}", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_list_attachments(args, token):
    entities = paginate_list(token, "attachment", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_attachment(args, token):
    result = api_get(token, f"attachment/{args.hash}")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Users, Authors, System Fields ---

def cmd_list_users(args, token):
    entities = paginate_list(token, "user", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_list_authors(args, token):
    entities = paginate_list(token, "author", {}, args.limit, args.paginate)
    print(json.dumps(entities, indent=2))


def cmd_get_system_fields(args, token):
    result = api_get(token, "system_field")
    print(json.dumps(result.get("result", result), indent=2))


# --- READ: Search (QQL) ---

def cmd_search(args, token):
    all_entities = []
    offset = 0
    limit = min(args.limit, 100)

    while True:
        params = {"query": args.query, "limit": limit, "offset": offset}
        result = api_get(token, "search", params)
        entities = result.get("result", {}).get("entities", [])
        all_entities.extend(entities)
        total = result.get("result", {}).get("count", 0)

        if not args.paginate or not entities or offset + len(entities) >= total:
            break

        offset += len(entities)

    print(json.dumps(all_entities, indent=2))


# --- WRITE: Runs ---

def cmd_create_run(args, token):
    payload = {"title": args.title}
    if args.description:
        payload["description"] = args.description
    if args.include_all:
        payload["include_all_cases"] = True
    elif args.cases:
        payload["cases"] = [int(c) for c in args.cases.split(",")]
    if args.plan_id:
        payload["plan_id"] = args.plan_id
    if args.env_id:
        payload["environment_id"] = args.env_id
    if args.milestone_id:
        payload["milestone_id"] = args.milestone_id
    result = api_post(token, f"run/{args.project}", payload)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_complete_run(args, token):
    result = api_post(token, f"run/{args.project}/{args.id}/complete")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


# --- WRITE: Results ---

def cmd_create_result(args, token):
    payload = {"case_id": args.case_id, "status": args.status}
    if args.time_ms:
        payload["time_ms"] = args.time_ms
    if args.comment:
        payload["comment"] = args.comment
    if args.stacktrace:
        payload["stacktrace"] = args.stacktrace
    if args.defect:
        payload["defect"] = True
    result = api_post(token, f"result/{args.project}/{args.run}", payload)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_bulk_results(args, token):
    data = load_json_arg(args.data)
    if isinstance(data, list):
        data = {"results": data}
    result = api_post(token, f"result/{args.project}/{args.run}/bulk", data)
    print(json.dumps(result.get("result", result), indent=2))


# --- WRITE: Test Cases ---

def cmd_create_case(args, token):
    payload = {"title": args.title}
    if args.suite_id:
        payload["suite_id"] = args.suite_id
    if args.milestone_id:
        payload["milestone_id"] = args.milestone_id
    if args.severity is not None:
        payload["severity"] = args.severity
    if args.priority is not None:
        payload["priority"] = args.priority
    if args.type is not None:
        payload["type"] = args.type
    if args.behavior is not None:
        payload["behavior"] = args.behavior
    if args.automation is not None:
        payload["automation"] = args.automation
    if args.status is not None:
        payload["status"] = args.status
    if args.layer is not None:
        payload["layer"] = args.layer
    if args.is_flaky is not None:
        payload["is_flaky"] = args.is_flaky
    if args.steps_type:
        payload["steps_type"] = args.steps_type
    if args.description:
        payload["description"] = args.description
    if args.preconditions:
        payload["preconditions"] = args.preconditions
    if args.postconditions:
        payload["postconditions"] = args.postconditions
    if args.tags:
        payload["tags"] = [t.strip() for t in args.tags.split(",")]
    result = api_post(token, f"case/{args.project}", payload)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_update_case(args, token):
    payload = {}
    if args.title:
        payload["title"] = args.title
    if args.suite_id:
        payload["suite_id"] = args.suite_id
    if args.milestone_id:
        payload["milestone_id"] = args.milestone_id
    if args.severity is not None:
        payload["severity"] = args.severity
    if args.priority is not None:
        payload["priority"] = args.priority
    if args.type is not None:
        payload["type"] = args.type
    if args.behavior is not None:
        payload["behavior"] = args.behavior
    if args.automation is not None:
        payload["automation"] = args.automation
    if args.status is not None:
        payload["status"] = args.status
    if args.layer is not None:
        payload["layer"] = args.layer
    if args.is_flaky is not None:
        payload["is_flaky"] = args.is_flaky
    if args.steps_type:
        payload["steps_type"] = args.steps_type
    if args.description:
        payload["description"] = args.description
    if args.preconditions:
        payload["preconditions"] = args.preconditions
    if args.postconditions:
        payload["postconditions"] = args.postconditions
    if args.tags:
        payload["tags"] = [t.strip() for t in args.tags.split(",")]
    result = api_patch(token, f"case/{args.project}/{args.id}", payload)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_bulk_cases(args, token):
    data = load_json_arg(args.data)
    if isinstance(data, list):
        data = {"cases": data}
    result = api_post(token, f"case/{args.project}/bulk", data)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_attach_external_issue(args, token):
    links = load_json_arg(args.links)
    payload = {"type": args.type, "links": links}
    result = api_post(token, f"case/{args.project}/external-issue/attach", payload)
    print(json.dumps(result.get("result", result), indent=2))


# --- WRITE: Defects ---

def cmd_create_defect(args, token):
    payload = {"title": args.title}
    if args.severity is not None:
        payload["severity"] = args.severity
    if args.actual_result:
        payload["actual_result"] = args.actual_result
    result = api_post(token, f"defect/{args.project}", payload)
    print(json.dumps(result.get("result", result), indent=2))


def cmd_resolve_defect(args, token):
    result = api_patch(token, f"defect/{args.project}/{args.id}/resolve")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


# --- DESTRUCTIVE: Deletes ---

def cmd_delete_case(args, token):
    result = api_delete(token, f"case/{args.project}/{args.id}")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


def cmd_delete_run(args, token):
    result = api_delete(token, f"run/{args.project}/{args.id}")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


def cmd_delete_result(args, token):
    result = api_delete(token, f"result/{args.project}/{args.hash}")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


def cmd_delete_defect(args, token):
    result = api_delete(token, f"defect/{args.project}/{args.id}")
    print(json.dumps({"status": result.get("status", False)}, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Qase REST API v1 client (API token auth)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command")

    def add_pagination(p):
        p.add_argument("--paginate", action="store_true", help="Fetch all pages")
        p.add_argument("--limit", type=int, default=100, help="Results per page (max 100)")

    def add_project(p):
        p.add_argument("--project", required=True, metavar="CODE", help="Project code, e.g. DEMO")

    # --- READ: Projects ---
    p = subparsers.add_parser("list-projects", help="List all projects")
    add_pagination(p)

    p = subparsers.add_parser("get-project", help="Get a specific project")
    add_project(p)

    # --- READ: Suites ---
    p = subparsers.add_parser("list-suites", help="List test suites in a project")
    add_project(p)
    add_pagination(p)

    p = subparsers.add_parser("get-suite", help="Get a specific suite")
    add_project(p)
    p.add_argument("id", type=int, help="Suite ID")

    # --- READ: Test Cases ---
    p = subparsers.add_parser("list-cases", help="List test cases in a project")
    add_project(p)
    p.add_argument("--suite-id", type=int, metavar="N", help="Filter by suite ID")
    p.add_argument("--search", metavar="TEXT", help="Filter by case title keyword")
    p.add_argument("--status", metavar="STATUS", help="Filter: actual, draft, deprecated (comma-separated)")
    p.add_argument("--milestone-id", type=int, metavar="N", help="Filter by milestone ID")
    p.add_argument("--severity", metavar="LIST",
                   help="Comma-separated: undefined,blocker,critical,major,normal,minor,trivial")
    p.add_argument("--priority", metavar="LIST",
                   help="Comma-separated: undefined,high,medium,low")
    p.add_argument("--type", metavar="LIST",
                   help="Comma-separated: other,functional,smoke,regression,security,usability,performance,acceptance")
    p.add_argument("--behavior", metavar="LIST",
                   help="Comma-separated: undefined,positive,negative,destructive")
    p.add_argument("--automation", metavar="LIST",
                   help="Comma-separated: is-not-automated,automated (legacy filter; response also has isManual/isToBeAutomated boolean fields)")
    add_pagination(p)

    p = subparsers.add_parser("get-case", help="Get full details for one test case")
    add_project(p)
    p.add_argument("id", type=int, help="Test case ID")

    # --- READ: Test Runs ---
    p = subparsers.add_parser("list-runs", help="List test runs in a project")
    add_project(p)
    p.add_argument("--status", metavar="STATUS", help="Filter: in_progress, passed, failed, aborted")
    add_pagination(p)

    p = subparsers.add_parser("get-run", help="Get full details for one test run")
    add_project(p)
    p.add_argument("id", type=int, help="Test run ID")
    p.add_argument("--include", metavar="LIST", help="Comma-separated: cases, defects")

    # --- READ: Results ---
    p = subparsers.add_parser("list-results", help="List test run results")
    add_project(p)
    p.add_argument("--run", type=int, metavar="N", help="Filter by run ID")
    p.add_argument("--case-id", type=int, metavar="N", help="Filter by case ID")
    p.add_argument("--status", metavar="STATUS", help="Filter: passed, failed, blocked, skipped, invalid")
    p.add_argument("--from-time", metavar="DATETIME", help='Start: "YYYY-MM-DD HH:MM:SS"')
    p.add_argument("--to-time", metavar="DATETIME", help='End: "YYYY-MM-DD HH:MM:SS"')
    add_pagination(p)

    p = subparsers.add_parser("get-result", help="Get a specific result by hash")
    add_project(p)
    p.add_argument("hash", help="Result hash (e.g. abc123def456)")

    # --- READ: Defects ---
    p = subparsers.add_parser("list-defects", help="List defects in a project")
    add_project(p)
    p.add_argument("--status", metavar="STATUS", help="Filter by defect status")
    add_pagination(p)

    p = subparsers.add_parser("get-defect", help="Get a specific defect")
    add_project(p)
    p.add_argument("id", type=int, help="Defect ID")

    # --- READ: Milestones, Plans, Environments ---
    p = subparsers.add_parser("list-milestones", help="List milestones in a project")
    add_project(p)
    add_pagination(p)

    p = subparsers.add_parser("list-plans", help="List test plans in a project")
    add_project(p)
    add_pagination(p)

    p = subparsers.add_parser("get-plan", help="Get a specific test plan")
    add_project(p)
    p.add_argument("id", type=int, help="Plan ID")

    p = subparsers.add_parser("list-environments", help="List environments in a project")
    add_project(p)
    add_pagination(p)

    # --- READ: Custom Fields, Shared Steps, Attachments ---
    p = subparsers.add_parser("list-custom-fields", help="List all custom fields")
    add_pagination(p)

    p = subparsers.add_parser("list-shared-steps", help="List shared steps in a project")
    add_project(p)
    add_pagination(p)

    p = subparsers.add_parser("list-attachments", help="List all attachments")
    add_pagination(p)

    p = subparsers.add_parser("get-attachment", help="Get an attachment by hash")
    p.add_argument("hash", help="Attachment hash")

    # --- READ: Users, Authors, System Fields ---
    p = subparsers.add_parser("list-users", help="List all users in the workspace")
    add_pagination(p)

    p = subparsers.add_parser("list-authors", help="List all authors")
    add_pagination(p)

    subparsers.add_parser("get-system-fields", help="Get all system field definitions")

    # --- READ: Search ---
    p = subparsers.add_parser("search", help="Search using QQL (Qase Query Language)")
    p.add_argument("--query", required=True,
                   help='QQL expression, e.g. entity = "case" and project = "DEMO"')
    add_pagination(p)

    # --- WRITE: Runs ---
    p = subparsers.add_parser("create-run", help="Create a new test run")
    add_project(p)
    p.add_argument("--title", required=True, help="Run title")
    p.add_argument("--description", metavar="TEXT", help="Run description")
    p.add_argument("--cases", metavar="1,2,3", help="Comma-separated case IDs to include")
    p.add_argument("--include-all", action="store_true", help="Include all cases in the project")
    p.add_argument("--plan-id", type=int, metavar="N", help="Create from a test plan")
    p.add_argument("--env-id", type=int, metavar="N", help="Environment ID")
    p.add_argument("--milestone-id", type=int, metavar="N", help="Milestone ID")

    p = subparsers.add_parser("complete-run", help="Complete (close) a test run")
    add_project(p)
    p.add_argument("id", type=int, help="Run ID")

    # --- WRITE: Results ---
    p = subparsers.add_parser("create-result", help="Report a result for one test case in a run")
    add_project(p)
    p.add_argument("--run", type=int, required=True, metavar="N", help="Run ID")
    p.add_argument("--case-id", type=int, required=True, metavar="N", help="Test case ID")
    p.add_argument("--status", required=True,
                   help="passed, failed, blocked, skipped, invalid")
    p.add_argument("--time-ms", type=int, metavar="N", help="Execution time in milliseconds")
    p.add_argument("--comment", metavar="TEXT", help="Comment")
    p.add_argument("--stacktrace", metavar="TEXT", help="Stacktrace")
    p.add_argument("--defect", action="store_true", help="Flag result as a defect")

    p = subparsers.add_parser("bulk-results", help="Bulk create results (JSON string or @filepath)")
    add_project(p)
    p.add_argument("--run", type=int, required=True, metavar="N", help="Run ID")
    p.add_argument("--data", required=True,
                   help='JSON array of result objects, or @filepath. '
                        'Each: {"case_id": N, "status": "passed", "time_ms": N, "comment": "..."}')

    # --- WRITE: Cases ---
    p = subparsers.add_parser("create-case", help="Create a test case")
    add_project(p)
    p.add_argument("--title", required=True, help="Case title")
    p.add_argument("--suite-id", type=int, metavar="N", help="Suite ID")
    p.add_argument("--milestone-id", type=int, metavar="N", help="Milestone ID")
    p.add_argument("--severity", type=int, metavar="N",
                   help="0=undefined 1=blocker 2=critical 3=major 4=normal 5=minor 6=trivial")
    p.add_argument("--priority", type=int, metavar="N",
                   help="0=undefined 1=high 2=medium 3=low")
    p.add_argument("--type", type=int, metavar="N",
                   help="0=other 1=functional 2=smoke 3=regression 4=security 5=usability 6=performance 7=acceptance")
    p.add_argument("--behavior", type=int, metavar="N",
                   help="0=undefined 1=positive 2=negative 3=destructive")
    p.add_argument("--automation", type=int, metavar="N",
                   help="0=manual 2=automated")
    p.add_argument("--status", type=int, metavar="N",
                   help="0=actual 1=draft 2=deprecated")
    p.add_argument("--layer", type=int, metavar="N",
                   help="0=unknown 1=e2e 2=api 3=unit")
    p.add_argument("--is-flaky", type=int, metavar="N",
                   help="0=no 1=yes")
    p.add_argument("--steps-type", metavar="TYPE",
                   help="classic (default) or gherkin")
    p.add_argument("--description", metavar="TEXT", help="Case description")
    p.add_argument("--preconditions", metavar="TEXT", help="Preconditions")
    p.add_argument("--postconditions", metavar="TEXT", help="Postconditions")
    p.add_argument("--tags", metavar="tag1,tag2", help="Comma-separated tags")

    p = subparsers.add_parser("update-case", help="Update an existing test case")
    add_project(p)
    p.add_argument("id", type=int, help="Test case ID")
    p.add_argument("--title", metavar="TEXT", help="Case title")
    p.add_argument("--suite-id", type=int, metavar="N", help="Suite ID")
    p.add_argument("--milestone-id", type=int, metavar="N", help="Milestone ID")
    p.add_argument("--severity", type=int, metavar="N",
                   help="0=undefined 1=blocker 2=critical 3=major 4=normal 5=minor 6=trivial")
    p.add_argument("--priority", type=int, metavar="N",
                   help="0=undefined 1=high 2=medium 3=low")
    p.add_argument("--type", type=int, metavar="N",
                   help="0=other 1=functional 2=smoke 3=regression 4=security 5=usability 6=performance 7=acceptance")
    p.add_argument("--behavior", type=int, metavar="N",
                   help="0=undefined 1=positive 2=negative 3=destructive")
    p.add_argument("--automation", type=int, metavar="N",
                   help="0=manual 2=automated")
    p.add_argument("--status", type=int, metavar="N",
                   help="0=actual 1=draft 2=deprecated")
    p.add_argument("--layer", type=int, metavar="N",
                   help="0=unknown 1=e2e 2=api 3=unit")
    p.add_argument("--is-flaky", type=int, metavar="N",
                   help="0=no 1=yes")
    p.add_argument("--steps-type", metavar="TYPE",
                   help="classic (default) or gherkin")
    p.add_argument("--description", metavar="TEXT", help="Case description")
    p.add_argument("--preconditions", metavar="TEXT", help="Preconditions")
    p.add_argument("--postconditions", metavar="TEXT", help="Postconditions")
    p.add_argument("--tags", metavar="tag1,tag2", help="Comma-separated tags")

    p = subparsers.add_parser("bulk-cases", help="Bulk create test cases (JSON string or @filepath)")
    add_project(p)
    p.add_argument("--data", required=True,
                   help='JSON array of case objects, or @filepath. '
                        'Each: {"title": "...", "suite_id": N, "severity": N, ...}')

    p = subparsers.add_parser("attach-external-issue",
                               help="Attach Jira (or other) issues to test cases")
    add_project(p)
    p.add_argument("--type", required=True,
                   help="Integration type: jira-cloud or jira-server")
    p.add_argument("--links", required=True,
                   help='JSON array of link objects, or @filepath. '
                        'Each: {"case_id": N, "issue_id": "PROJECT-123"}')

    # --- WRITE: Defects ---
    p = subparsers.add_parser("create-defect", help="Create a defect")
    add_project(p)
    p.add_argument("--title", required=True, help="Defect title")
    p.add_argument("--severity", type=int, metavar="N",
                   help="1=blocker 2=critical 3=major 4=normal 5=minor 6=trivial")
    p.add_argument("--actual-result", metavar="TEXT", help="Actual result description")

    p = subparsers.add_parser("resolve-defect", help="Resolve a defect")
    add_project(p)
    p.add_argument("id", type=int, help="Defect ID")

    # --- DESTRUCTIVE: Deletes ---
    p = subparsers.add_parser("delete-case", help="[DESTRUCTIVE] Delete a test case")
    add_project(p)
    p.add_argument("id", type=int, help="Test case ID")

    p = subparsers.add_parser("delete-run", help="[DESTRUCTIVE] Delete a test run")
    add_project(p)
    p.add_argument("id", type=int, help="Run ID")

    p = subparsers.add_parser("delete-result", help="[DESTRUCTIVE] Delete a result by hash")
    add_project(p)
    p.add_argument("hash", help="Result hash")

    p = subparsers.add_parser("delete-defect", help="[DESTRUCTIVE] Delete a defect")
    add_project(p)
    p.add_argument("id", type=int, help="Defect ID")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    token = load_credentials()

    commands = {
        # Read
        "list-projects":    cmd_list_projects,
        "get-project":      cmd_get_project,
        "list-suites":      cmd_list_suites,
        "get-suite":        cmd_get_suite,
        "list-cases":       cmd_list_cases,
        "get-case":         cmd_get_case,
        "list-runs":        cmd_list_runs,
        "get-run":          cmd_get_run,
        "list-results":     cmd_list_results,
        "get-result":       cmd_get_result,
        "list-defects":     cmd_list_defects,
        "get-defect":       cmd_get_defect,
        "list-milestones":  cmd_list_milestones,
        "list-plans":       cmd_list_plans,
        "get-plan":         cmd_get_plan,
        "list-environments": cmd_list_environments,
        "list-custom-fields": cmd_list_custom_fields,
        "list-shared-steps": cmd_list_shared_steps,
        "list-attachments": cmd_list_attachments,
        "get-attachment":   cmd_get_attachment,
        "list-users":       cmd_list_users,
        "list-authors":     cmd_list_authors,
        "get-system-fields": cmd_get_system_fields,
        "search":           cmd_search,
        # Write
        "create-run":       cmd_create_run,
        "complete-run":     cmd_complete_run,
        "create-result":    cmd_create_result,
        "bulk-results":     cmd_bulk_results,
        "create-case":      cmd_create_case,
        "update-case":      cmd_update_case,
        "bulk-cases":       cmd_bulk_cases,
        "attach-external-issue": cmd_attach_external_issue,
        "create-defect":    cmd_create_defect,
        "resolve-defect":   cmd_resolve_defect,
        # Destructive
        "delete-case":      cmd_delete_case,
        "delete-run":       cmd_delete_run,
        "delete-result":    cmd_delete_result,
        "delete-defect":    cmd_delete_defect,
    }

    commands[args.command](args, token)


if __name__ == "__main__":
    main()
