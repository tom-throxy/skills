import glob
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone

# Many concurrent sessions start in the same repo; nudge each repo at most this often.
NUDGE_EVERY_S = 4 * 3600
MAX_LINES = 8


def git(cwd, *args):
    try:
        return subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def repo_slug(cwd):
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?/?$", git(cwd, "remote", "get-url", "origin"))
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    common = git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return os.path.basename(os.path.dirname(common)) if common else ""


def frontmatter(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return {}
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    fields = {}
    for line in match.group(1).splitlines() if match else []:
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def parse_time(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def describe(fields):
    where = ", ".join(v for v in (fields.get("services"), fields.get("paths")) if v)
    return f"{fields.get('id', '?')} (PR #{fields.get('pr', '?')}{'; ' + where if where else ''})"


def main():
    payload = json.load(sys.stdin)
    slug = repo_slug(payload.get("cwd", "."))
    if not slug:
        return 0
    claude_home = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.expanduser("~/.claude")
    ledger = os.path.join(claude_home, "ship-metrics", slug)
    if frontmatter(os.path.join(ledger, "config.md")).get("metrics") == "off":
        return 0
    nudge = os.path.join(ledger, ".last_nudge")
    if os.path.exists(nudge) and time.time() - os.path.getmtime(nudge) < NUDGE_EVERY_S:
        return 0

    now = datetime.now(timezone.utc)
    lines = []
    for path in sorted(glob.glob(os.path.join(ledger, "open", "*.md"))):
        fields = frontmatter(path)
        evaluate_from = parse_time(fields.get("evaluate_from", ""))
        evaluate_by = parse_time(fields.get("evaluate_by", ""))
        created = parse_time(fields.get("created", ""))
        if evaluate_by and evaluate_by < now:
            lines.append(f"- overdue: {describe(fields)}")
        elif evaluate_from and evaluate_from <= now:
            lines.append(f"- due: {describe(fields)}")
        elif fields.get("status") == "awaiting-merge" and created and now - created > timedelta(days=1):
            lines.append(f"- confirm merged: {describe(fields)}")
        elif fields.get("agreed") == "pending":
            lines.append(f"- awaiting user agreement: {describe(fields)}")
    if not lines:
        return 0

    open(nudge, "w").close()
    extra = len(lines) - MAX_LINES
    body = "\n".join(lines[:MAX_LINES] + ([f"- ...and {extra} more"] if extra > 0 else []))
    context = (
        f"Ship metrics need attention in {slug} (ledger: {ledger}):\n{body}\n"
        "Evaluate them with the ship-metrics skill when this session's work touches them "
        "or the user asks; otherwise mention them to the user once."
    )
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
