# Design lens

The questions a staff engineer asks of a design, used by `design-grill` (before code) and `design-review` (after code). Each section gives the questions, what to look for in a diff, and common patterns and anti-patterns to name.

**Name patterns to teach the why.** Naming a pattern ("this is a dual write"), with a short reason it matters, helps the user learn to spot it themselves and gives them a term to look up. Only name a pattern that genuinely fits; a forced label is worse than none.

## Contents

0. Calibrate first: stakes and reversibility
1. Intent and business impact
2. Choice provenance
3. Simplicity and coupling
4. Implicit contracts
5. Lifespan, migration and maintenance
6. Scale and cost
7. Operability

Domain packs, loaded only when the change touches them: `domains/api.md`, `domains/data.md`, `domains/infra.md`, `domains/async.md`.

---

## 0. Calibrate first: stakes and reversibility

Do this before asking anything. It sets how deep every later question goes, and it is what stops design review from becoming a nitpick list.

**Stakes profile.** Who uses this, and what happens when it fails?

| Profile | Examples | Tolerates |
|---|---|---|
| External, money or safety | consumer payments, billing, medical, auth | almost no correctness, durability or audit debt |
| External, product | customer-facing features, client APIs | debt in internals, not in contracts or data |
| Internal, operational | admin tools, ops dashboards, back-office tooling | simple and suboptimal, if failures are visible |
| Internal, analytical | reporting, analytics, batch jobs | stale data, slow queries, rerunnable failures |

The same design choice can be fine in one profile and negligent in another. A nightly analytics job that silently drops a row costs a slightly wrong chart. A payment flow that does the same loses money and trust. State the profile you assumed; if it is a guess, that is a question.

**Reversibility.** Scrutiny scales with how hard a choice is to undo:

- **One-way doors** get deep questioning: database schemas and stored data formats, public or cross-team APIs, event and message contracts, infra topology, third-party vendor lock-in, anything users learn to rely on.
- **Two-way doors** get one pass at most: internal function shape, module layout, UI copy, config values, anything behind a flag.

## 1. Intent and business impact

- What is this trying to achieve, and for whom? Which user problem or business outcome does it serve?
- What metric shows it is working? Can that metric actually be measured once this ships?
- Which users, segments or flows are **not** covered? Which existing flows does it change or break: other roles, edge-case accounts, legacy data, mobile, other locales or time zones?
- What data does it leave behind: rows written but never read, records that existing data cannot reach, history not migrated, fields that go unpopulated for old records?
- What does it cost: infra spend, third-party usage fees, operational load, support tickets, the on-call burden?
- What happens to users if it ships half-working?

In review, the blind phase infers the intent from the code. The informed phase compares that against the stated intent. A mismatch is a finding either way: the code does something nobody asked for, or it fails to show what it was for.

## 2. Choice provenance

For each significant choice (a library, a data shape, a sync or async boundary, an algorithm, a service split):

- What was the obvious alternative? Was this chosen over it consciously, by default, or for lack of knowledge of the alternative?
- Is it the simplest thing that works for the actual requirement?
- Does it build for scope nobody asked for (extension points, config, generality)?
- Or is it too brittle for change that is already expected?

Patterns: **YAGNI**; **speculative generality**; **golden hammer** (using the familiar tool because it is familiar); **not-invented-here**; **cargo culting** (copying a pattern without its reason); **Chesterton's fence** (removing something without knowing why it was there).

## 3. Simplicity and coupling

Simpler-to-understand beats theoretically optimal until a stated requirement says otherwise.

- **Couple or decouple?** Split into separate services, queues or deployables only for a concrete reason: independent scaling, independent deploy cadence, separate ownership, or failure isolation. Otherwise keep it in-process. A split without one of those reasons is cost with no benefit.
- **Algorithms:** a simple O(n²) or a full scan is fine when the input is bounded and small. Name the bound ("at most ~200 seats per account") so a reader knows when it stops being fine.
- **Abstraction:** an abstraction with one implementation and no second one coming is indirection. Three similar call sites may be better left duplicated than forced through a shared helper.
- **Moving parts:** each new datastore, queue, cache or service is something to run, monitor, upgrade and debug at 3am. Is the existing stack enough?

Patterns: **distributed monolith** (services that must deploy together); **microservice envy**; **premature optimisation**; **premature abstraction**; **wrong abstraction** (a shared helper growing flags per caller); **rule of three**; **boring technology**; **modular monolith**.

## 4. Implicit contracts

What does the change assume, without saying so, about:

- **Callers**: input shape, call frequency, ordering, concurrency, that they retry, that they don't?
- **Dependents**: services, jobs, dashboards or exports reading the data or API this touches. Does anything downstream read a field whose meaning just changed?
- **Upstreams**: latency, availability, rate limits, response shape, idempotency of the services it calls?
- **The environment**: clock and time zone, single instance versus many, process lifetime, filesystem, region?

For each assumption: how does it break, how would anyone notice, and what is the blast radius?

Patterns: **Hyrum's law** (every observable behaviour becomes a dependency); **temporal coupling** (must be called in order); **leaky abstraction**; **thundering herd**; **retry storm**; **at-least-once delivery**; **idempotency**.

## 5. Lifespan, migration and maintenance

- Is this meant to last years, or is it a stopgap? Says who? Stopgaps tend to become permanent, so if it is one, what will replace it, and when?
- What changes are expected here in the near and medium term? Does the design leave seams where those changes will land, without building for them now?
- How will this be upgraded, migrated or removed later? Simpler infra (managed services, fewer components, standard tooling) makes later upgrades cheaper.
- **When must the debt be paid?** Shortcuts are fine until a trigger: before it reaches high-stakes users, before data volume makes migration expensive, when the area's change rate rises, or before another team builds on it. Name the trigger.

Patterns: **expand-contract** (parallel change) for safe migrations; **strangler fig** for incremental replacement; **feature flag** or **branch by abstraction**; **technical debt quadrant** (deliberate versus inadvertent, prudent versus reckless); **temporary permanence**.

## 6. Scale and cost

- What is the load today, and what growth is expected, in orders of magnitude (10x? 1000x?) and over what horizon? Design for the next order of magnitude, not the third.
- What grows without bound: tables, queues, fan-out per event, payload size, per-tenant data?
- What is on the hot path? What runs per request, versus per batch or per day?
- How does cost scale with usage: linearly, per tenant, per event? Is any third-party call priced per use?
- How will the data or resources be queried and used later, and does the shape support that?

Patterns: **N+1 queries**; **unbounded fan-out**; **hot partition** or **hot key**; **back-pressure**; **load shedding**; **cost per tenant**.

## 7. Operability

- How will anyone know it is working, and know when it is not? Is the success metric from section 1 measurable from logs or metrics this change emits?
- What does failure look like to whoever is on call: an alert, a log line, a silent gap?
- How is it rolled out (flag, percentage, all at once), and how is it rolled back? Does the rollback survive data already written in the new shape?
- Is there a manual operation someone will need (a rerun, a backfill, a replay), and is it possible without a code change?

Patterns: **dark launch**; **canary**; **kill switch**; **observability-driven development**; **runbook**.
