---
name: tidy-comments
description: Strict lead-engineer review of code comments in a diff, removing or rewriting every comment that is not brief, neutral, durable and genuinely insightful. Use before committing, before opening or updating a PR (prepare-pr runs this first), when the user asks to clean up, trim, tidy or review comments, docstrings or JSDoc, or says the code is over-commented. Also use after writing a substantial change, before showing the diff to the user.
---

# Tidy comments

Bad comments are the first thing a human reviewer trips over. Each one costs reading time, invites a review round-trip, and later rots into a lie. A comment has to earn its place. The default verdict is **delete**.

Review as a demanding lead engineer, not as the author. The author of a comment always thinks it is helpful, so judge each one as if a stranger wrote it.

## Scope

Review comments in the change, not the whole codebase:

1. Every comment added or modified in the diff against the base branch, plus uncommitted work. Use `git diff <base>...HEAD` and `git diff HEAD`. Find the base with `gh pr view --json baseRefName` if a PR exists, otherwise the repo's default branch.
2. Every pre-existing comment on a line the change touched. Once edited, it is the change's responsibility.
3. Every pre-existing comment that the change made stale or wrong. Cut it to its surviving fact, or delete it.

Leave untouched comments elsewhere alone. Rewriting unrelated code adds diff noise to the review.

Docstrings, JSDoc, `@doc`/`@moduledoc`, rustdoc, type annotations in comments and config-file comments all count.

## The bar

Keep a comment only if all of these hold:

- **It gives genuine insight the code cannot.** It answers a question a competent reader would have after reading the code. Typical survivors: a non-obvious invariant, a constraint from outside the code (a provider limit, a spec quirk, a platform bug), or why the obvious simpler approach is wrong. A good test: would a plausible "simplification" break something if this comment were gone?
- **It is brief.** One line by default. Several lines only for a genuinely non-recoverable invariant.
- **It is neutral and impersonal.** A plain statement of fact, in passive or declarative voice. No "I", "we", "you", "let's".
- **It does not editorialise.** No "deliberately", "importantly", "note that", "load-bearing", "hack", "nice", "clean", emphasis capitals or exclamation marks. State the fact; the reader judges its importance.
- **It references nothing outside the code.** No tickets, PRs, incidents, plans, phases, increments, steps, review rounds, people's names, Slack threads or measurements from a one-off run. That history belongs in the PR description or commit message.
- **It will not go stale.** No names of other functions, files, paths, modules, services or callers that this code does not itself depend on. If the code is agnostic to who calls it, the comment must be too. No "used by X" or "called from Y".

Two kinds of comment always fail, whatever the file or codebase does:

- File header comments: banners, file summaries, licence-style blurbs the repo does not mandate, "this file contains..." module docs.
- Separator comments: `// ---- helpers ----`, `# === Section ===`, `/* region */`.

Codebase convention does not justify a bad comment. If the surrounding file is full of narration, do not match it. Your lines still meet the bar.

### Decision comments

A comment may record a decision **the user consciously made** that a later reader would otherwise "fix". These are rare. They carry a date and a reason, in one line:

```python
# 2026-11-10: retries capped at 3; the payment provider flags accounts that retry more.
```

Decisions the agent made on its own do not go in code comments. They go in the PR description's assumptions list, where the reviewer can challenge them.

## Verdicts

For each comment in scope, pick one:

- **Delete**: the default. Use it for narration of the next lines, restated names, types or guards, TODOs with no owner or trigger, commented-out code, and anything failing the bar.
- **Rewrite**: the comment holds one real insight buried in noise. Cut it to that insight in one line. Do not reword it at the same length.
- **Keep**: passes every point above unchanged.

If deleting a comment loses information the reviewer needs (why a workaround exists, which incident prompted it), move that information to the PR description or commit message, not back into the code.

## Examples

```ts
// Loop through the users and filter out inactive ones
const active = users.filter(u => u.active);
```
Delete. It narrates the code.

```ts
// IMPORTANT: we deliberately use a Map here (see PERF-412) because lookups were slow
```
Rewrite or delete. The ticket, the editorialising and "we" all go. Keep only a fact the reader cannot infer, if one exists. Here none survives, so delete.

```python
# Called by the nightly sync job in services/sync/runner.py
def reconcile(accounts): ...
```
Delete. It names a caller and a path, and it goes stale the day either moves.

```go
// Stripe returns amounts in the smallest currency unit; JPY has no minor unit.
```
Keep. It holds an external constraint that a "simplification" dividing by 100 would break.

```js
// ===== Helpers =====
```
Delete. Separators never pass.

## Process

1. Collect the in-scope comments from the diff.
2. Give each a verdict against the bar. Be harsh. Expect most agent-written comments to be deleted.
3. Apply the edits. Do not change any code behaviour while doing so.
4. If the changes were already committed, commit the cleanup as its own commit, for example `chore: tidy comments`. Never amend or rewrite history for it.
5. Report briefly: counts of deleted, rewritten and kept comments. List any information you moved to the PR description, and any comment you kept that a reviewer might query.
