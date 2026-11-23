# State files

All state lives in `~/.claude/monitor-system/<workspace>/`. All timestamps are ISO 8601 UTC. The user may hand-edit `profile.md` and the `classification` and `note` fields in the ledger. Respect their edits over your own inferences.

| File | Purpose | Written |
|---|---|---|
| `profile.md` | Sources, identities, services, ticket mapping | First run, then when the user corrects it or a new tool appears |
| `ledger.json` | Per-signal history and noise classification | Every run |
| `issues.json` | Issues already handled, and what the user was told | Every run |
| `history.jsonl` | One snapshot line per run, used for baselines | Appended every run, pruned to 14 days on a sweep |
| `lock` | Contains the start timestamp of the run in progress | Created at run start, deleted at run end |

## profile.md

```markdown
# monitor-system profile: <workspace>
Confirmed by user: <date>

## User
- Ticket tracker: <user ref, e.g. "me">
- Code host: <login>
- Chat: <handle>

## Sources
| Role | Tool | What to query | Notes |
|---|---|---|---|
| alerts | <tool> | <e.g. monitors in alert/warn/no-data; event stream> | |
| metrics | <tool> | <golden signals per service, below> | |
| logs | <tool> | <index, or how to group by pattern> | |
| errors | <tool> | <new groups, regressions> | |
| chat | <tool> | <#incidents, #alerts-prod> | read-only |
| tickets | <tool> | <team/project> | |
| deploys | <tool> | <workflow, or deploy event source> | |

Missing roles: <role: what that hides>

## Services
| Service | Criticality | Repo | Key signals (query) | Limits |
|---|---|---|---|---|

## Monitors as code
<repo/path and format, or "none: propose UI changes to user">

## Tickets
- Team/project: <...>
- Urgent = <tool's name> · High = <tool's name>
- Labels: <optional>

## Notify
- Urgent issues: <push notification | DM to <user> via <tool> | report only>
```

## ledger.json

```json
{
  "signals": {
    "<signature>": {
      "source": "<tool>",
      "name": "<monitor or error name>",
      "link": "<url>",
      "severity": "<platform severity>",
      "daily_fires": { "2026-11-22": 14, "2026-11-21": 12 },
      "last_response": "<timestamp or null>",
      "response_kind": "ack | reply | ticket | incident | commit | null",
      "classification": "signal | noise | ignored | unknown",
      "note": "<why it got this classification>",
      "cleanup": { "status": "pr | proposed | declined | done", "ref": "<url>", "date": "<date>" }
    }
  }
}
```

Keep `daily_fires` to the last 14 days. A `declined` cleanup is never proposed again.

## issues.json

```json
{
  "issues": {
    "<slug>": {
      "title": "<symptom-first title>",
      "signatures": ["<signature>"],
      "class": "active | degradation | watching",
      "priority": "urgent | high | none",
      "ticket": "<url or null>",
      "prs": ["<url>"],
      "research": "none | running | done",
      "status": "open | mitigated | resolved",
      "first_seen": "<timestamp>",
      "last_seen": "<timestamp>",
      "last_reported": "<timestamp>",
      "reported_state": "<one line: what the user was last told>"
    }
  }
}
```

Compare the current state with `reported_state` to decide whether anything is new enough to report.

## history.jsonl

One line per run:

```json
{"ts": "<timestamp>", "mode": "tick | sweep", "window": "<start>/<end>", "counts": {"<source>": 12}, "snapshots": {"<service>.<metric>": 0.42}, "issues": ["<slug>"], "blind": ["<source>"]}
```

Record the same metrics on every sweep, so the daily values line up for trend projection.
