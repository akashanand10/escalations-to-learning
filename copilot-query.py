#!/usr/bin/env python3
"""
copilot-query.py — Programmatically query GitHub Copilot CLI about this project.

Uses the VS Code-bundled `copilot` CLI in non-interactive mode (-p) to send
prompts and get responses. Can read project files, run commands, and analyze data.

Usage:
  # Simple query
  ./copilot-query.py "What escalation tickets were analyzed in March 2026?"

  # Query with file context piped in
  cat analysis/bp-engineering-escalations-march-2026-analysis.md | ./copilot-query.py "Summarize the top 3 issues"

  # Query with explicit file reference
  ./copilot-query.py "List all ticket keys from this file" -f analysis/bp-engineering-escalations-march-2026-analysis.md

  # JSON output for scripting
  ./copilot-query.py "List ticket keys as a JSON array" --json

  # Higher reasoning effort
  ./copilot-query.py "Analyze trends across Feb and March reports" --effort high

  # Allow tools (file read, shell) for richer answers
  ./copilot-query.py "How many test cases exist in the ABP Qase project?" --tools

  # Dry run — just print the command
  ./copilot-query.py "What is this project?" --dry-run
"""

import argparse
import os
import subprocess
import sys

COPILOT_BIN = os.path.expanduser(
    "~/Library/Application Support/Code/User/globalStorage/"
    "github.copilot-chat/copilotCli/copilot"
)


def find_copilot():
    """Locate the copilot binary."""
    # 1. Check PATH first
    from shutil import which
    path_bin = which("copilot")
    if path_bin:
        return path_bin
    # 2. Check VS Code's bundled location
    if os.path.isfile(COPILOT_BIN) and os.access(COPILOT_BIN, os.X_OK):
        return COPILOT_BIN
    return None


def build_command(args, prompt):
    """Build the copilot CLI command list."""
    copilot = find_copilot()
    if not copilot:
        print(
            "Error: copilot CLI not found. Ensure VS Code with GitHub Copilot Chat is installed.",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd = [copilot, "-p", prompt, "-s"]

    if args.effort:
        cmd += ["--effort", args.effort]

    if args.json:
        cmd += ["--output-format", "json"]

    if args.model:
        cmd += ["--model", args.model]

    if args.tools:
        cmd.append("--allow-all-tools")

    if args.allow_all:
        cmd.append("--allow-all")

    return cmd


def main():
    parser = argparse.ArgumentParser(
        description="Query GitHub Copilot CLI about this project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("prompt", nargs="?", help="The prompt/question to send to Copilot")
    parser.add_argument(
        "-f", "--file",
        action="append",
        default=[],
        help="Include file content in the prompt (can be repeated)",
    )
    parser.add_argument(
        "--effort",
        choices=["low", "medium", "high", "xhigh"],
        help="Reasoning effort level",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON Lines format",
    )
    parser.add_argument(
        "--model",
        help="Specify AI model (e.g. gpt-4o, claude-sonnet-4)",
    )
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Allow Copilot to use tools (read files, run shell commands)",
    )
    parser.add_argument(
        "--allow-all",
        action="store_true",
        help="Allow all permissions (tools, paths, URLs)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the command that would be executed, don't run it",
    )

    args = parser.parse_args()

    # Build prompt from arguments + stdin + file contents
    parts = []

    # Check for piped stdin
    if not sys.stdin.isatty():
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            parts.append(f"Here is the input data:\n\n{stdin_data}\n")

    # Include file contents
    for filepath in args.file:
        if not os.path.isfile(filepath):
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        with open(filepath) as f:
            content = f.read()
        parts.append(f"Contents of {filepath}:\n\n{content}\n")

    # Add the user prompt
    if args.prompt:
        parts.append(args.prompt)
    elif not parts:
        parser.print_help()
        sys.exit(1)

    prompt = "\n\n".join(parts)

    cmd = build_command(args, prompt)

    if args.dry_run:
        # Print shell-escaped command
        import shlex
        print(shlex.join(cmd))
        sys.exit(0)

    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
