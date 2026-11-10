import json
import os
import re
import sys
import tempfile

SIGNATURE = "Agent-generated description"
MESSAGE = (
    "Blocked by the prepare-pr gate. Before opening a PR, invoke the prepare-pr skill: "
    "tidy comments, write the PR description in its format, then present the summary. "
    "Re-run `gh pr create` afterwards; this gate only blocks once per session."
)


def body_file_text(command, cwd):
    match = re.search(r"(?:--body-file|-F)[ =](\"[^\"]+\"|'[^']+'|\S+)", command)
    if not match:
        return ""
    path = os.path.join(cwd, os.path.expanduser(match.group(1).strip("'\"")))
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def main():
    payload = json.load(sys.stdin)
    command = payload.get("tool_input", {}).get("command", "")
    if not re.search(r"\bgh\s+pr\s+create\b", command):
        return 0
    if SIGNATURE in command or SIGNATURE in body_file_text(command, payload.get("cwd", ".")):
        return 0

    # Blocks once per session only, so a deliberate departure from the format cannot loop.
    marker_dir = os.path.join(tempfile.gettempdir(), "prepare-pr-gate")
    os.makedirs(marker_dir, exist_ok=True)
    marker = os.path.join(marker_dir, re.sub(r"[^\w-]", "_", payload.get("session_id", "unknown")))
    if os.path.exists(marker):
        return 0
    open(marker, "w").close()
    print(MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
