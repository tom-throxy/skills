# skills

Plugins live in `plugins/` and install through the marketplace. Standalone skills live in `skills/` and install with the `skills` CLI.

## Plugins

The `pr` plugin covers shipping a feature end to end, from planning through design review to a reviewer-ready PR. Its `ship-metrics` skill names, for each change, the metric it should move and when to check it. It then tracks those metrics after merge in a ledger under the agent's home folder (`~/.claude/ship-metrics/` for Claude Code), and checks them off.

Add the marketplace and install the plugin in Claude Code:

```
/plugin marketplace add tom-throxy/skills
/plugin install pr@tom-skills
```

## Standalone skills

- `monitor-system`: a tool-agnostic first responder. It watches your observability, alert, incident and ticket channels, tickets and researches real issues, opens fix PRs, and cleans up noisy observability on quiet runs. Run it once with `/monitor-system`, or on a loop with `/loop /monitor-system`.

Install a skill globally:

```
npx skills add tom-throxy/skills --skill monitor-system -g
```
