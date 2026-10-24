# Agent instructions

These instructions apply across the repository. Use the linked documents for detailed review criteria and task-specific workflows.

## Branches and diffs

- Start each new repository task on a new branch from the current `main`; never commit task changes directly to `main`. Keep follow-up edits for an existing PR on its topic branch and explicitly target the branch for writes.
- Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.

## Deferred retrospective notes

- Treat `#retro` notes as deferred observations, not immediate task instructions. Until the user explicitly starts a retrospective, continue the current task without debating or implementing them. At the start of a retrospective, collect and group the notes, compare them with concrete evidence, and decide which changes to accept, reject, or defer. Notes are scoped to the current conversation unless the user asks to preserve them elsewhere.

## Technical documentation

- Before writing or reviewing technical documentation, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md).
- Inspect relevant files and nearby documentation. Keep each concept in its established location and link to its canonical explanation instead of duplicating it.
