# Stacked PRs

Read this only when the user has asked for stacked PRs, either directly or through a memory or CLAUDE.md rule. Stacking exists to make review easier. If a split does not make any PR easier to review, do not make it.

If the user has not opted in and a single PR runs into the thousands of changed lines (excluding generated files) and splits cleanly, mention stacking in the "Needs you" list. Do not restructure on your own.

## Plan the layers

Classify every changed file, then group the files into PRs. Order the PRs bottom to top by dependency.

1. **Generated files go in their own PR at the top of the stack.** A reviewer can then skip that PR entirely. Generated files include codegen output, API clients, ORM or migration snapshots, protobuf and GraphQL output, lockfiles, build artefacts, recorded fixtures and snapshot files. Where possible, keep the source that produces them (the schema, the `.proto`, the `package.json` change) out of the generated PR. That source is what deserves review, so it belongs in the lower PR whose logic it serves.
2. **Logically separate, significant changes get their own PR.** Make the split when a piece is non-trivial and can stand apart from the rest of the work, such as a schema migration plus its data layer, a new shared library, or a refactor that later work relies on. Trivial changes (a renamed helper, a one-line config tweak) ride along with whatever needs them.
3. **Keep stacks small.** Most stacks have 1, 2 or 3 PRs, not counting the generated PR. Too many PRs is its own review burden: each one needs context loaded, and changes ripple through the stack.
4. **Ask before going further.** A non-generated PR may still run into the thousands of changed lines while it could be split further along a logical seam. In that case, propose the extra split to the user and wait for an answer before restructuring. Show each proposed PR's scope and rough line count.

Moving the generated source and output apart can leave lower PRs failing CI. It can also break the main branch if a lower PR merges before the generated PR. When that happens, say so in each affected PR's "Deployment" section, for example: "Merge together with #125 (generated); `main` will not build with this PR alone." Repeat it in the user's "Needs you" list.

## Restructure the branch

Splitting existing commits into layered branches rewrites history. If the branch is already pushed and shared, or holds other people's commits, confirm with the user first. Never merge a base branch into a child to restack. Rebase instead.

Run the design review and the comment pass (prepare-pr steps 2 and 3) once, across the whole change, before splitting. That way design fixes and comment cleanup are not scattered across layers.

## Open the stack

- **If `gh stack` is available** (`gh extension list` shows `github/gh-stack`), use it, together with the gh-stack skill if it is installed. `gh stack submit --auto` creates the PRs with generated titles. Afterwards, set each PR's real title and body with `gh pr edit <n> --title ... --body-file ...`.
- **Otherwise**, create one branch per layer, each branched from the one below. Open each PR with `--base` set to the branch below it; the bottom PR targets the main branch.

## Describe each PR

Every non-generated PR gets the full prepare-pr description, scoped to its own diff. Start each body with a stack line, so a reviewer landing on any PR can see where it sits:

```markdown
Stack: #123 (this) → #124 → #125 (generated)
```

The generated PR gets a minimal body: the stack line, which PR(s) it is generated for, and the exact command that regenerates it, so a reviewer can verify it without reading it. Example:

```markdown
Stack: #123 → #124 → #125 (this, generated)

Generated output for #123 and #124. No review needed.
Regenerate with: `pnpm codegen && pnpm install`
```
