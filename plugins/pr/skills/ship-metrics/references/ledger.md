# Ledger formats

The ledger folder is `<agent home>/ship-metrics/<owner>-<repo>/`. The agent home is `${CLAUDE_CONFIG_DIR:-~/.claude}` for Claude Code; any other agent uses its own config home.

```
config.md
open/<pr>-<slug>.md     one file per metric that hasn't been checked yet
done/<pr>-<slug>.md     checked metrics, deleted after 30 days
```

Write every timestamp in ISO 8601 UTC. Frontmatter is flat `key: value` lines, with lists comma-separated on one line. The session-start hook parses frontmatter line by line, so don't use nested YAML. The user may hand-edit any file. Their edits win over your own inferences.

## config.md

```markdown
---
metrics: on
set_by: inferred
updated: 2026-11-24
---
Reason: deploys to prod via .github/workflows/deploy.yml; Datadog monitors checkout-api.
Deploy signal: merge to main deploys automatically via deploy.yml (about 8 min). Use the workflow run's finish time as deployed_at.
Measurement tools: Datadog (logs, APM, metrics), Linear team SHOP (bug reports), gh.
```

`metrics` is `on` or `off`, and `set_by` is `inferred` or `user`. If the deploy signal is unknown, use `merged_at` as `deployed_at`, and say that in the verdict.

## open/<pr>-<slug>.md

```markdown
---
id: 412-null-cart
repo: acme/shop
pr: 412
pr_url: https://github.com/acme/shop/pull/412
kind: fix
status: awaiting-merge
agreed: yes
created: 2026-11-24T10:02Z
merged_at:
deployed_at:
read_after: 1d
evaluate_from:
evaluate_by:
services: checkout-api
paths: src/checkout/, src/cart/cart.ts
evaluating_by:
expiry_raised:
---

**Metric:** checkout 5xx caused by NullCartError
**Expect:** 0/day
**Baseline:** ~40/day, 7-day mean to 2026-11-24, measured 2026-11-24
**How to measure:** Datadog logs, count of `service:checkout-api @error.kind:NullCartError`, daily rollup
**Why:** the fix guards the empty-cart path that throws
```

The fields:

- `kind` is `fix`, `outcome` or `guard`.
- `status` is `awaiting-merge`, `watching` or `evaluating`.
- `agreed` is `yes`, or `pending` for an unattended run whose metrics the user hasn't confirmed yet.
- `read_after` is `0d` for an immediate reading, or `Nd` for N days after deploy.

When the PR merges, fill in the dates:

- `evaluate_from`: `deployed_at` plus `read_after`. For an immediate reading, use `deployed_at` plus 1 hour, or longer for low-traffic paths.
- `evaluate_by`: `evaluate_from` plus 7 days. Within that grace period a late reading is still fair.

## Verdict

When you check a metric, append this to its file, then move the file to `done/`:

```markdown
## Verdict: met
Evaluated: 2026-11-26T09:10Z
Measured: 0/day over 2026-11-25..2026-11-26 (baseline ~40/day)
Confounds: none on checkout-api in the window (checked: ledger, git log on paths, deploys)
```

The verdict is `met`, `not met`, `inconclusive` or `expired`.

## PR body section

`prepare-pr` writes this section, using the same metric lines as the plan:

```markdown
### Ship metrics
<!-- ship-metrics:v1 -->
- **m1** fix · checkout 5xx from NullCartError · expect 0/day (baseline ~40/day over 7d) · read 1d after deploy · Datadog logs `service:checkout-api @error.kind:NullCartError`
```

## Verdict comment

Post this on the PR once it has a verdict:

```markdown
<!-- ship-metrics:verdict 412-null-cart -->
**Ship metric m1: met.** NullCartError 5xx is 0/day over 2026-11-25..26 (baseline ~40/day). No confounding changes on checkout-api in the window.
```

## Rebuilding the ledger

This applies on another machine, in a cloud session, or when the ledger folder is missing. Rebuild it from the PRs:

```bash
gh pr list --state all --search '"Ship metrics" in:body' --limit 100 \
  --json number,url,state,mergedAt,createdAt,body
```

Keep the PRs whose body contains `<!-- ship-metrics:v1 -->` and that were created in the last 45 days. For each metric line in such a PR, look for a matching `ship-metrics:verdict` comment on the PR (`gh pr view <n> --json comments`). If there is none, write an `open/` file for that metric. Do the same before evaluating on a machine whose ledger may be stale, so two machines never post two verdicts for the same metric.
