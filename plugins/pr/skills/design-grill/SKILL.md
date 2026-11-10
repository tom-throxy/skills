---
name: design-grill
description: Questions a planned feature or change on architecture, design and business impact before any code is written. Asks only what the codebase and its conventions cannot answer, in small themed batches, each with a recommended answer, a short reason and the pattern at stake, and flags scope creep for an explicit fold-in or defer decision. Use this whenever the user asks to plan, design, scope, spec or think through an approach for a feature, migration, integration or refactor ("plan this", "how should we build X", "let's design", "write a plan for"). Run it alongside any other planning skill or plan mode, before the plan is written, even when the user does not ask to be questioned.
---

# Design grill

The cheapest time to fix a design is before it is built. This skill asks the architectural, design and business questions a staff engineer would ask of a plan, so that the user decides the things that matter consciously instead of inheriting the agent's defaults.

It is not a design interview. A question earns a place only if two things hold: the codebase does not already answer it, and its answer would change the design.

The questions come from the shared lens at `../../references/design-lens.md` (relative to this skill's directory). Read it first. Then read only the domain packs in `../../references/domains/` that the planned change touches: `api.md`, `data.md`, `infra.md`, `async.md`.

## 1. Learn before asking

Before asking the user anything, find what is already settled:

- The request itself, and anything the user has already said about goals, users and constraints.
- Codebase standards: CLAUDE.md, AGENTS.md, ADRs, contributing docs, memories, and lint or architecture rules.
- How similar features are already built here: their data shape, API style, job framework, and infra.
- Existing planning artefacts and where the team keeps them: a `plans/` or `.plans/` folder, `docs/adr/`, a ticket tracker named in memories or CLAUDE.md, or a ticketing MCP that is connected.

Anything settled here is not a question. Note it as "decided by the codebase" so the user sees what was assumed and why.

## 2. Calibrate

Settle the stakes profile and the reversibility of the main choices (lens section 0). Use them to rank everything that follows. A one-way door on a high-stakes path gets asked first. Two-way doors usually do not get asked at all: pick the sensible default, and list it as an assumption.

If the stakes profile is not obvious from the request and the codebase, make it the first question. Every other answer depends on it.

## 3. Draft and filter questions

Walk the lens and the relevant domain packs, and draft candidate questions about this specific plan. Then cut hard:

- **Cut** anything the codebase, its conventions or the user's earlier words already answer.
- **Cut** anything whose answer would not change the design, the scope or the plan.
- **Cut** generic questions that would fit any feature ("have you considered scalability?"). Make each one concrete: "Seat counts per account are under 50 today. Do you expect enterprise accounts in the thousands within a year? That decides whether seat checks can be a scan."
- **Keep** questions where you would otherwise silently pick a default that the user might well disagree with.

Typical survivors cover:
- intent and success metrics;
- users or flows not covered;
- the expected lifespan;
- near-term changes the design should leave room for;
- growth and how the data will be queried;
- whether to couple or split;
- when a deliberate shortcut must be repaid.

## 4. Ask in themed batches

Group the surviving questions into batches of about 2-4 that share a theme, for example "Who it's for and what success looks like", "Data shape and growth", or "Lifespan and future change". Ask the highest-stakes batch first.

Each question carries:

- **The question**, concrete to this plan.
- **A recommended answer**, with a one or two sentence reason, so the user can accept it quickly.
- **The pattern at stake**, where one genuinely fits, named with a few words on why it matters. For example: "This is a **dual write**. If the publish fails after the commit, the event is lost silently." Naming the pattern helps the user learn to spot it themselves.
- **A `scope creep` flag**, if answering it the "better" way means refactoring or building beyond the request (see below).

If `AskUserQuestion` is available, use one call per batch, with the batch theme as the header. Put the recommended option first, marked "(Recommended)", and put the reason and the pattern in its description. Otherwise, ask in plain text with the same structure.

After each batch, fold the answers in. Ask a follow-up batch only if the answers opened a new design-changing question. **Stop** when no remaining question would change the design. Most plans need one to three batches; a long session means the filter was too loose.

## 5. Scope creep

Some questions expose a better design that the request did not ask for. For example: "this could build on the existing RBAC, but a proper permissions system would serve it better." Still ask these, because the user should know. Flag each one as **scope creep** and give the cost of both sides: what folding it in adds now, and what deferring it costs later, including the trigger that would force it (lens section 5).

The user decides, for each item:

- **Fold in**: it becomes part of the plan, with the scope change stated.
- **Defer**: it goes on the future-improvements list.

Never fold a refactor in on your own.

## 6. Record the outcome

Write a short decision record wherever this codebase keeps planning artefacts: the plan file if a planning skill is writing one, a `plans/` or ADR folder, or tickets if memories or CLAUDE.md say the team tracks work there. If there is no convention, keep it in the conversation.

```markdown
## Design decisions (<YYYY-MM-DD>)
- Stakes: <profile>, <one line on why>
- <decision> - <reason> (user)
- <default accepted> - <reason> (agent default, accepted)
- Decided by codebase: <convention followed>

## Future improvements
- <deferred item> - <why deferred> - <trigger that makes it due>
```

Capture deferred items using the codebase's own mechanism: tickets if the team tickets, TODOs if that is the convention, otherwise this list. `prepare-pr` later carries them into the PR's follow-ups section. Decisions marked "(user)" are the user's, and they do not need re-litigating in review.

Then continue with the planning itself, built on these answers.
