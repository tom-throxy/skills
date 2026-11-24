---
name: prepare-pr
description: Makes a pull request cheap for a human to understand and review. For non-trivial changes it runs a blind design review first. Then it runs a strict comment pass, writes a short structured PR description (assumptions, mermaid data-flow diagram, API/DB changes, deploy risks, follow-ups, with the full agent write-up collapsed), optionally splits the work into stacked PRs, and gives the user a terse summary with a review-focus list. Use this whenever a PR is about to be opened, created, raised, submitted or pushed for review, whether the user asks ("open a PR", "make a PR", "ship it", "put this up for review", "raise PRs for this") or you decide to open one yourself as part of a larger task. Run it before any `gh pr create` or `gh stack submit`, and when asked to rewrite or tidy an existing PR description.
---

# Prepare PR

A reviewer's attention is the scarcest resource in the loop. Agents write long, thorough PR descriptions, and humans skim them and miss the parts that need them. This skill makes a PR quick to understand. It surfaces the decisions the agent made on its own, and it makes plain where the human must act, in review or in deployment.

## Workflow

### 1. Gather context

- Base branch, commits, and `git diff --stat <base>...HEAD`. Include uncommitted work the user means to ship.
- **The user's own words about this PR**: the request, the goal, any framing they gave. The title and intro reuse or paraphrase these, because the reviewer often is the user, and their words are how they think about the change.
- Which decisions the user made and which you made on your own. Your own choices become the assumptions list. If `design-grill` left a decision record, it already separates the two, and lists deferred future improvements.
- Whether the user wants stacked PRs: a direct instruction this session, or a memory or CLAUDE.md rule. If they do, read `references/stacking.md` now and follow it alongside the steps below.
- A repo PR template (`.github/pull_request_template.md` or similar). If one exists, keep its required sections and checklists, and fit the structure below around them.

### 2. Design review

For a non-trivial change, invoke the `design-review` skill; it defines what counts as non-trivial. It goes before the comment pass because its fixes can change code. Its outcome feeds the description: agent decisions go into the assumptions, open questions go into "Needs you", and deferred items go into follow-ups. For a trivial change, skip it.

### 3. Comment pass

Invoke the `tidy-comments` skill on the branch diff. If it is unavailable, apply its rules directly: delete every comment that is not brief, neutral, durable and genuinely insightful. Carry any history it moves out of the code (incidents, tickets, measurements) into the PR description.

### 4. Write the description

Write it to a temporary file and pass it with `--body-file`. This avoids shell-quoting damage to the mermaid and markdown.

**Title**: one line saying what the PR does, in the user's terms where possible. The title is the header, so do not repeat it in the body.

**Body**, in this order. Drop any optional section that does not apply instead of writing "N/A", except deployment, where "None." tells the reviewer it was considered.

````markdown
<2-4 short lines: the objective, and briefly how this PR achieves it. Reuse or paraphrase the user's own description of the work.>

### Assumptions & decisions
- <assumption or design decision the agent made without explicit direction, and the reason in a few words>
- <...>

### Data flow
```mermaid
<high-level diagram: only when the PR does I/O, network calls, or talks to other services>
```

### API & schema changes
- `POST /v1/orders` - <one line: what changed>
- `postgres` `orders` - <one line: column added, index dropped, etc.>

### Deployment
- <risk, manual step, ordering constraint, env var, migration, flag flip, backfill, or post-deploy check, each saying who or what must act>

### Ship metrics
<!-- ship-metrics:v1 -->
- **m1** <kind> · <metric> · expect <direction and size> (baseline <value over window>) · read <timeline> · <tool> `<query>`

### Follow-ups
- <deferred improvement or scope-creep item> - <trigger that makes it due> - <link to ticket or TODO, if captured there>

<details>
<summary>Agent-generated description</summary>

<the full, detailed write-up: changes by area, reasoning, alternatives considered, testing done and not done, edge cases, anything moved out of code comments>

</details>
````

Guidance for each section:

- **Intro**: say what the PR is for and the mechanism, not a changelog. If the user said "add retry so webhook failures stop dropping orders", lead with that.
- **Assumptions & decisions**: this is the section the reviewer most needs, so make it honest. List what you guessed, chose between, or defaulted on: naming, error handling strategy, a library picked, a behaviour you inferred, scope you left out. Skip decisions the user explicitly directed, unless a reviewer could not follow the PR without them. Aim for 2-6 bullets.
- **Data flow**: include it only if the PR adds or changes I/O, network requests, queues, storage or calls to other services. Keep it to the services and stores involved, about 10 nodes at most, not the internal call graph. Mark what is new or changed so the eye goes straight to it:

  ```mermaid
  flowchart LR
    client[Web app] --> api[API]
    api -->|new: enqueue| q[(orders queue)]
    q -->|new| worker[Order worker]
    worker -->|changed: retries| psp[Payment provider]
    worker --> db[(Postgres)]
    classDef changed stroke:#d97706,stroke-width:2px
    class q,worker changed
  ```

- **API & schema changes**: use the form `` `METHOD /route` - change `` for HTTP, RPC or GraphQL surfaces, and `` `db` `table` - change `` for schemas and migrations. Include breaking changes, new required fields, and changed status codes. Omit the section if nothing changed.
- **Deployment**: anything a human must do or watch. Examples: run a migration before deploy, set a new secret, a deploy-ordering dependency on another service, a feature flag to flip, a backfill, a metric or log line to check after release, a known risk and its blast radius. Name the action plainly; "Set `STRIPE_WEBHOOK_SECRET` in prod before deploy" beats "configuration may be required".
- **Ship metrics**: the metrics agreed during planning, in the `ship-metrics` skill's format, with the marker comment kept so the ledger can be rebuilt from PRs. Omit the section if the plan recorded "No ship metric", or if ship metrics are off for the repo. If they are on and the plan named none for a change in runtime behaviour, propose them now (`ship-metrics` step 2).
- **Follow-ups**: deferred improvements from `design-grill` or `design-review`, and known debt this PR takes on deliberately. Link each to where it is captured, if the codebase tickets or uses TODOs. Omit the section if there are none.
- **Details block**: this is where the thoroughness goes. Write it fully; it costs the reviewer nothing because it is collapsed. The summary text stays exactly `Agent-generated description`.

### 5. Open the PR

Open it with `gh pr create --title ... --body-file <file>`, or `gh pr edit` for an existing PR. Respect the user's choice of draft or ready, base branch, reviewers and labels. Opening a PR publishes the branch, so push only what the user asked to ship.

If a hook blocked `gh pr create` and pointed you here, that is expected. Complete steps 1-4, then re-run the command.

Once the PR exists, record its ship metrics in the ledger (`ship-metrics` step 3).

### 6. Report to the user

The user may have been away while you worked, and the PR is now theirs to review. Give them a terse briefing in the terminal, shorter than the PR body. Use plain text and ASCII, because mermaid does not render in a terminal.

```
PR #<n>: <title>
<url>

- Aim: <what it achieves, one line>
- How: <mechanism, one line>
- Changes: <only the kinds that apply: APIs, DB, data flows, logic, user flows; one line each>
- Ship metrics: <one line each: metric, expected move, when it is read; omit if none>

<ASCII service diagram of the change, new or changed parts marked>

- <one bullet per change in the diagram: what changed and why>

Needs you:
- <decisions to confirm, open design-review questions and scope-creep choices, assumptions to check, ship metrics marked `agreed: pending`, deploy or post-deploy actions; "Nothing beyond review" if none>

Review focus:
- `path/to/file.ext` `functionOrModule` - <why it deserves attention: core logic, risky edge, assumption encoded here>
```

ASCII diagram style:

```
[Web app] --> [API] --(new: enqueue)--> ((orders queue)) --> [Order worker]*
                                                                  |
                                                    (retries*)    v
                                                          [Payment provider]
* = new or changed
```

For a PR with no service-level interaction, draw the module or component flow it changes. For a trivial PR (a typo, a version bump), skip the diagram.

**Review focus**: 3-6 entries, ordered by where a reviewer's minutes matter most. Lead with core logic, places that encode an assumption, and risky edge cases. Leave out tests, generated files and mechanical renames unless something in them is subtle.

For a stack, list every PR with its number, URL and base first. Then give one summary for the whole stack, and the review focus grouped by PR.
