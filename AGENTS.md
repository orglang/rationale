# Agent instructions

These instructions apply across the repository. Use the linked documents for detailed review criteria and task-specific workflows.

## Branch and change discipline

- Start every task that changes repository content in a new branch based on the current `main`; do not make task commits directly on `main`. Use an explicit branch name for every write and keep follow-up edits for the same PR on its existing topic branch.
- Keep changes scoped to the requested outcome. Prefer small, targeted edits over reconstructing or rewriting an entire document from partial excerpts.
- Before finishing or committing, inspect the complete diff against the branch base, not just the edited passage. Check for accidental whitespace changes, missing blank lines or list-item boundaries, and unrelated content changes. Verify the final text around each edit.
- Group related semantic updates together when dependent summaries or cross-references must stay consistent; the number of changed locations alone is not a reason to omit necessary consistency updates.

## Deferred retrospective notes

- Treat `#retro` notes as deferred observations, not immediate task instructions. Until the user explicitly starts a retrospective, continue the current task without debating or implementing them. At the start of a retrospective, collect and group the notes, compare them with concrete evidence, and decide which changes to accept, reject, or defer. Notes are scoped to the current conversation unless the user asks to preserve them elsewhere.

## Technical documentation

- Before writing or reviewing technical documentation, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md).
- Inspect the relevant files and nearby documentation. Keep each concept in its established location and link to its canonical explanation instead of duplicating it.
- Keep changes within the requested scope. Before finishing, review the diff and remove unrelated edits.
