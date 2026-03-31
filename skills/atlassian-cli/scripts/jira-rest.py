#!/usr/bin/env python3
"""
jira-rest.py — Backup Jira REST API v3 client using Basic Auth (email + API token).

Usage:
  python3 jira-rest.py search --jql "project = BP" [--paginate] [--limit N]
  python3 jira-rest.py view BP-1234 [--fields "*all"]

Credentials (first match wins):
  1. Env vars: JIRA_SITE, JIRA_EMAIL, JIRA_TOKEN
  2. ~/.jira-credentials  (KEY=VALUE lines, lines starting with # are comments)

Get an API token at: https://id.atlassian.com/manage/api-tokens

Output:
  search → JSON array of issue objects  [{key, fields: {...}}, ...]
            (same structure as Jira REST API issues array — compatible with
             jira-extract-list.jq and `jq -r '.[].key'`)
  view   → JSON object {key, fields: {...}}
            (raw Jira REST API response — compatible with jira-extract-detail.jq)
"""

import sys
import os
import json
import argparse
import urllib.request
import urllib.parse
import urllib.error
import base64

CREDENTIALS_FILE = os.path.expanduser("~/.jira-credentials")
BASE_API = "rest/api/3"


# ---------------------------------------------------------------------------
# Credentials
# ---------------------------------------------------------------------------

def load_credentials():
    creds = {
        "JIRA_SITE": os.environ.get("JIRA_SITE"),
        "JIRA_EMAIL": os.environ.get("JIRA_EMAIL"),
        "JIRA_TOKEN": os.environ.get("JIRA_TOKEN"),
    }

    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                if key in creds and not creds[key]:
                    creds[key] = value

    missing = [k for k, v in creds.items() if not v]
    if missing:
        print(f"Error: Missing credentials: {', '.join(missing)}", file=sys.stderr)
        print(f"Set them as env vars or add to {CREDENTIALS_FILE}:", file=sys.stderr)
        print(f"  JIRA_SITE=paylocity.atlassian.net", file=sys.stderr)
        print(f"  JIRA_EMAIL=you@company.com", file=sys.stderr)
        print(f"  JIRA_TOKEN=<token from https://id.atlassian.com/manage/api-tokens>", file=sys.stderr)
        sys.exit(1)

    return creds["JIRA_SITE"].rstrip("/"), creds["JIRA_EMAIL"], creds["JIRA_TOKEN"]


def make_auth_header(email, token):
    raw = f"{email}:{token}".encode()
    return f"Basic {base64.b64encode(raw).decode()}"


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _request(method, url, auth_header, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": auth_header,
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


def api_get(site, auth_header, path, params=None):
    url = f"https://{site}/{BASE_API}/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    return _request("GET", url, auth_header)


def api_post(site, auth_header, path, data):
    url = f"https://{site}/{BASE_API}/{path}"
    return _request("POST", url, auth_header, data)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_search(args, site, auth_header):
    """Search for issues using JQL. Outputs a JSON array of issue objects."""
    all_issues = []
    next_page_token = None
    max_per_page = min(args.limit, 100)  # API cap is 100

    while True:
        payload = {
            "jql": args.jql,
            "maxResults": max_per_page,
            "fields": [
                "summary", "status", "assignee", "priority",
                "issuetype", "reporter", "created", "comment",
            ],
        }
        if next_page_token:
            payload["nextPageToken"] = next_page_token

        result = api_post(site, auth_header, "search/jql", payload)
        issues = result.get("issues", [])
        all_issues.extend(issues)

        if not args.paginate or result.get("isLast", True) or not issues:
            break

        next_page_token = result.get("nextPageToken")
        if not next_page_token:
            break

    print(json.dumps(all_issues, indent=2))


def cmd_view(args, site, auth_header):
    """Fetch full details for a single issue. Outputs the raw Jira API response."""
    params = {"fields": "*all"}
    result = api_get(site, auth_header, f"issue/{args.key}", params)
    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Backup Jira REST API client (Basic Auth / API token)"
    )
    subparsers = parser.add_subparsers(dest="command")

    # search
    sp = subparsers.add_parser("search", help="Search issues with JQL")
    sp.add_argument("--jql", required=True, help="JQL query string")
    sp.add_argument("--paginate", action="store_true", help="Fetch all pages")
    sp.add_argument("--limit", type=int, default=100, help="Results per page (max 100)")

    # view
    vp = subparsers.add_parser("view", help="Get full details for one issue")
    vp.add_argument("key", help="Issue key, e.g. BP-1234")
    vp.add_argument("--fields", default="*all", help="Fields to include (default: *all)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    site, email, token = load_credentials()
    auth_header = make_auth_header(email, token)

    if args.command == "search":
        cmd_search(args, site, auth_header)
    elif args.command == "view":
        cmd_view(args, site, auth_header)


if __name__ == "__main__":
    main()
