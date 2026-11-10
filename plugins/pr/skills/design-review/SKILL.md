---
name: design-review
description: Adversarial self-review of a change's architecture, design and business impact before it ships. A blind subagent infers what the change is for and questions every significant choice (conscious or default? simplest that works? too brittle? what does it assume about users and other services?). The informed agent then checks that against the real intent and business context, fixes clear defects, and surfaces the rest for the user with the patterns at stake named. Use before opening a PR for any non-trivial change (prepare-pr runs it automatically), and whenever the user asks for a design, architecture or systems review of their own work, or asks "is this the right approach", "sanity-check the design", or "what will this break".
---

# Design review

Bug-hunting reviews ask whether the code does what it was meant to. This one asks whether it should do it this way, and what it assumes about users, data and other services that nobody wrote down. It is self-review: the goal is to catch design errors before a human reviewer, or production, does.

The questions come from the shared lens at `../../references/design-lens.md` (relative to this skill's directory), plus the domain packs in `../../references/domains/` that the diff touches: `api.md`, `data.md`, `infra.md`, `async.md`.

## When it runs

`prepare-pr` invokes this for non-trivial changes. Treat a change as non-trivial if it does any of the following:
- adds or alters a schema, migration or stored data format;
- adds or alters a public, cross-service or cross-team API, event or payload contract;
- adds or alters infra, deploy config or a new dependency on an external service;
- adds new I/O, a queue, a job or cron, or a third-party integration;
- introduces a new module or service boundary;
- changes more than roughly 300 non-generated, non-test lines of logic.

Skip it for docs, copy, test-only changes, dependency bumps and a bug fix confined to one function. Say in one line that it was skipped and why.

## Phase 1: blind review (subagent)

Spawn one subagent with the `Agent` tool. It sees the code only: no conversation, no plan, no PR description, no commit messages. Blindness is the point. If the code alone does not show what it is for, or shows something different from what was intended, that is a finding. An agent told the intent tends to read the code as achieving it.

Give it this brief, filled in:

```
You are a staff engineer doing an adversarial design review of a change you know nothing about.

Repo: <absolute path>. Diff: `git diff <base>...HEAD` plus `git diff HEAD`.
Read <absolute path to design-lens.md> and these domain packs: <paths, only those the diff touches>.
Read any source in the repo you need for context. Do NOT read plan files (plans/, .plans/, docs/plans), PR descriptions, commit messages, or ticket references; infer everything from the code.

Report, tersely:
1. Inferred intent: what this change is for, who it serves, and how it achieves it. Mark guesses.
2. Stakes and reversibility: your assumed stakes profile, and which choices are one-way doors.
3. Implicit assumptions: about callers, dependents, upstream services, data and environment. For each, how it breaks and the blast radius.
4. Choice questions: for each significant choice, give the choice, the obvious alternative, and whether it looks conscious or defaulted; whether it is the simplest thing that works, speculative, or brittle; and the named pattern or anti-pattern, only if one genuinely fits.
5. Business gaps: users, flows or existing data that look uncovered or broken; cost or operational load.
Rank by severity times irreversibility. Skip style, naming and bugs that are local to one line; other reviews cover those.
```

## Phase 2: informed triage (you)

Now bring in everything the subagent lacked: the user's words, the plan, the `design-grill` decision record, the PR description draft, and the business context from the conversation, memories and docs.

1. **Compare intents.** Set the subagent's inferred intent beside the real one. Where they differ, decide which is true. Either the code drifted from the goal, or it fails to show its purpose (unclear naming or structure), or the subagent misread it.
2. **Apply the business lens** (lens section 1) with the real context. Who is affected, which flows and existing data are not covered, what it costs, and does it move the success metric. A blind reviewer can only guess at this, so it is your job.
3. **Triage every finding** into one of:
   - **Resolved**: the context answers it (a recorded user decision, a codebase convention, an explicit requirement). Drop it.
   - **Defect**: a clear in-scope design error with an obvious fix that does not change the agreed approach, such as a missing idempotency key, a missing index on the new query, or an unhandled existing-data case. Fix it now.
   - **Needs user**: a real question about a choice the user should own, or a fix that would change the agreed approach. Do not decide it yourself.
   - **Scope creep**: a better design that goes beyond the request. Give the cost of folding it in now against deferring it, and the trigger that would make it due. The user decides; deferred items are captured the codebase's way (tickets, TODOs, or the PR's follow-ups section).
4. Be adversarial with the subagent's output too. Drop speculative findings that do not survive the real context, rather than passing noise on to the user.

## Report

Keep it short. The user reads this before, or alongside, the PR summary.

```
Design review: <n> fixed, <n> need you, <n> scope creep

Fixed:
- <what was wrong> -> <fix>  (<pattern>)

Needs you:
- <question>? Recommend: <answer>, because <reason>. (<pattern>: <why it matters, a few words>)

Scope creep:
- <improvement> - now: <cost>; defer: <cost>, due when <trigger>. Fold in or defer?

Intent check: <matches | drifted: one line>
```

Name a pattern only where it genuinely fits. The name, with a few words on why it matters, is there to help the user learn to spot it themselves.

When `prepare-pr` is running, feed the outcome into it:
- design decisions the agent made, and defaults the user accepted, go into "Assumptions & decisions";
- open "Needs you" items and scope-creep choices go into the user summary's "Needs you" list;
- deferred items go into the "Follow-ups" section.
