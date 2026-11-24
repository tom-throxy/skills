---
name: ship-metrics
description: Names the metric each change should move (or must not move), by roughly how much and by when, then tracks it after merge and checks it off. While planning it proposes 1-3 concrete, measurable metrics, each with a baseline, a direction, a rough size and a timeline, and agrees them with the user. prepare-pr carries them into the PR, and a shared ledger that any agent can read tracks the open ones. Due metrics are evaluated with confounding work taken into account, and misses go to the user for triage. Use this when planning or scoping any change to runtime behaviour (a bug fix, performance work, a feature on an existing path), when opening a PR, and when merging or watching one deploy. Use it before starting work in a repo, to check for open metrics on the same code. Also use it whenever the user asks "did that fix work", "check the metrics", "what's still outstanding from what we shipped", or "is anything regressing from recent merges", even if they don't name this skill.
---

# Ship metrics

When many PRs merge in a day, it gets hard to track what has been fixed, what worked, what didn't, and which concurrent sessions are pushing on the same thing. If each change names, before merge, the number it should move, the agent has a target to aim for. Later, anyone can tell whether the change landed.

This is not a gate and not a grade. Many effects can only be measured in production. A metric that doesn't move as expected is information about the system, not a failure of the work. Keep it light: if a step adds ceremony without making the outcome clearer, skip it.

## Where things live

Read `references/ledger.md` for the file formats.

- **Ledger**: `<agent home>/ship-metrics/<owner>-<repo>/`. For Claude Code, the agent home is `${CLAUDE_CONFIG_DIR:-~/.claude}`. For other agents, use that agent's own config home, such as `~/.codex`. Take `<owner>-<repo>` from the `origin` remote. Without a remote, use the name of the main checkout's directory, not the worktree's. The ledger sits outside the repo, so every worktree and concurrent session of the same agent shares it. Different agents each keep their own ledger, and the verdict comments on PRs keep them from checking the same metric twice. Each open metric gets its own file in `open/`, so concurrent writers never clobber each other. Checked metrics move to `done/`.
- **Config**: `config.md` in the same folder. It records whether metrics are on for this repo, how deploys happen, and which tools measure what.
- **PR body**: the permanent record of what was expected, in a `### Ship metrics` section.
- **Verdict comment** on the PR: the permanent record of the result. It also tells another machine or agent that a metric has already been checked.

## 0. Is it on?

Read `config.md`. If it is missing, infer the setting once and write it:

- **On**: the repo runs something with users. Signs include a deploy workflow, infrastructure as code, configured monitoring or error tracking, a connected observability tool that knows the service, an org-owned remote, or a tracker that receives bug reports.
- **Off**: a personal project, prototype, scratch repo or anything with no running service or users.

Record `set_by: inferred`, and tell the user in one line: "Ship metrics are on for this repo (deploys via `deploy.yml`, Datadog connected). Say 'turn off ship metrics' to change." When the user turns it on or off, record `set_by: user`. Never re-infer over the user's setting.

On first setup, also fill in the deploy signal and the measurement tools. They make every later evaluation cheaper.

When metrics are off, stop, unless the user explicitly asks to set or check one.

## 1. Recall before starting work

Before planning or editing in a repo with metrics on, list `open/` and read each file's frontmatter. Look for overlap with the work you're about to do: shared `paths`, or the same service, route or metric even through different files.

- **Overlap with a due metric**: evaluate it first (step 5), because your change will muddy the reading.
- **Overlap with a metric that isn't due yet**: note it in the plan as a confound. For example: "PR #412 expects checkout p50 down 20% by Friday, and this change touches the same handler." If your change would make that reading worthless, tell the user so they can decide the order of the work.

## 2. Propose during planning

First decide whether the change deserves a metric. Skip it when the change doesn't alter runtime behaviour (docs, tests, CI, internal tooling, a pure refactor), or when the only honest metric is "nothing breaks" and no specific signal is at risk. Write "No ship metric: <reason>" as one line in the plan, so the omission is visible and deliberate.

Otherwise propose 1-3 metrics. More than that is theatre. They come in three kinds:

- **fix**: the symptom stops. An error or log line drops to zero or below a level after deploy, or no further user or ticket reports of the bug arrive within N days.
- **outcome**: a number moves. Examples are latency percentiles, rows or bytes processed, cost, queue age, or a conversion step.
- **guard**: nothing the change could break moves. Use this kind for additive work that isn't trying to improve anything. Pick the one or two signals most at risk, and a tolerance: "`GET /v1/orders` p50 rises by no more than 10%."

Every metric needs four things:

- **How to measure it**: a tool, and a query or command that someone else can run unchanged. Prefer one that already exists, such as a monitor, a dashboard widget or a saved log query. If nothing can measure what matters, say so. That is an observability gap, which can become a follow-up. It is not a reason to invent a vague metric.
- **A baseline**: the current value, measured now over a comparable window. Use the same length, and be aware of weekday effects. A later reading means nothing without a baseline. If the tool isn't reachable now, capture the baseline when the PR opens, or before merge at the latest.
- **An expectation**: the direction and a rough size, such as "down 50% or more", "0 occurrences" or "within +10%". Rough is fine. The size is what separates a real effect from noise.
- **A timeline**: when to read it. The default is immediate: as soon as there is enough traffic after deploy, usually within hours. Otherwise give it in days, chosen so there's enough volume to tell. A bug seen 5 times a day can be read after 1-2 days; one reported weekly needs 2-3 weeks. Past 30 days the signal is too sparse to be worth tracking, so pick a different metric or skip it.

Agree the metrics with the user. Put them in the plan, or in the `design-grill` batch about success, with a recommended set the user can accept, edit, drop or add to. In an unattended run with no one to ask, record `agreed: pending`, and raise the metrics under "Needs you" in the PR summary. Evaluate them anyway.

Format in the plan:

```
Ship metrics
- m1 fix · checkout 5xx from NullCartError · expect 0/day (baseline ~40/day over 7d) · read 1d after deploy · Datadog logs `service:checkout-api @error.kind:NullCartError`
- m2 guard · POST /v1/cart p50 · expect at most +10% (baseline 82ms over 7d) · read immediately · Datadog APM p50 of `service:checkout-api resource_name:"POST /v1/cart"`
```

## 3. Record when the PR opens

`prepare-pr` adds the `### Ship metrics` section to the PR body. Once the PR exists, write one ledger file per metric to `open/` with `status: awaiting-merge`. If a baseline is still missing, measure it now. If review changes a metric, update both the PR body and the ledger file.

## 4. Watch during the merge

If you are seeing the PR through merge and deploy, and a metric's timeline fits inside this session, keep watching after the deploy. Read the metric once enough traffic has arrived (often 30-60 minutes on a busy route), then evaluate it with step 5 before you finish.

Otherwise, fill in `merged_at`, `deployed_at`, `evaluate_from` and `evaluate_by`, set `status: watching`, and leave the metric to the ledger.

## 5. Evaluate due metrics

This step runs when:
- a session-start note lists due metrics;
- the user asks;
- step 1 finds an overlapping due metric;
- a `monitor-system` sweep runs;
- the merge watch in step 4 reaches its reading.

For each metric:

1. **Refresh.** For `awaiting-merge`, run `gh pr view <n> --json state,mergedAt`. If the PR closed unmerged, delete the file. If it merged, fill in the dates (see `references/ledger.md`). If the metric is still not due, stop here.
2. **Claim.** Skip the metric if another session set `evaluating_by` within the last hour. Otherwise set it to yourself. Then check the PR for an existing verdict comment. If one exists, the metric was checked elsewhere: move the file to `done/` with that verdict.
3. **Measure.** Run the recorded query over the window after deploy. Match the baseline's window length and weekday mix where you can.
4. **Look for confounds.** List what else in the window could have moved this metric:
   - other ledger entries on the same service or paths, open or done;
   - `git log --since=<deployed_at> -- <paths>`, and other merges to the same service;
   - deploys, incidents and flag changes;
   - traffic shifts and seasonality.

   Name the confounds you found, and the ones you checked for but didn't find.
5. **Give a verdict.**
   - **met**: the metric moved as expected, or the guard held, and the confounds don't explain it.
   - **not met**: it didn't move, moved the wrong way, or broke the guard's tolerance, and the confounds don't explain it.
   - **inconclusive**: there was too little volume, the measurement broke, or the confounds could account for the result either way.

   If you find yourself arguing for a verdict, it is inconclusive.
6. **Record it.** Append the verdict to the ledger file and move the file to `done/`. Post the verdict comment on the PR.
7. **Report it.**
   - **met**: one line.
   - **not met**: raise it for triage. Say what was expected, what you measured, which confounds you checked and what the likely reasons are. Then offer options: accept it, open a follow-up, revert, or measure again later. Keep the wording neutral, because the change may still be right.
   - **inconclusive**: say why, and offer to extend the window, change the metric or drop it.

```
Ship metrics · <owner>/<repo> · <n> checked · <n> need you
- NOT MET · #418 m1 orders p50 · +23% vs expected at most +10% (baseline 82ms) · confounds: #421 also changed the orders handler (ruled out: deployed 2d later) · options: follow-up to profile serializer | revert | accept
- inconclusive · #420 m1 import rows/min · 14 runs since deploy, need ~50 · extend to 2026-12-01?
- met · #412 m1 NullCartError 0/day (baseline ~40/day)
Still open: <n> · next due: #425 m1 on 2026-11-28
```

List the metrics that need the user first.

## 6. Expiry and history

If `evaluate_by` passes with no evaluation, evaluate the metric now if a late reading still means something. If it doesn't, raise it once: "m1 on #412 was never checked and its window has passed. Check it late, or drop it?" Then record `expiry_raised`. If it is still open the next time you see it, move it to `done/` with the verdict `expired`. Raising it once is enough; don't nag.

Delete files in `done/` older than 30 days. Until then they matter. They are confounds for newer metrics. When a regression shows up, a recent "met" fix on the same service is a strong lead.
