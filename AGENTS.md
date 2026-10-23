# Agent instructions

These instructions apply across the repository. Use the linked documents for detailed review criteria and task-specific workflows.

## Deferred retrospective notes

- Treat `#retro` notes as deferred observations, not immediate task instructions. Until the user explicitly starts a retrospective, continue the current task without debating or implementing them. At the start of a retrospective, collect and group the notes, compare them with concrete evidence, and decide which changes to accept, reject, or defer. Notes are scoped to the current conversation unless the user asks to preserve them elsewhere.

## Technical documentation

- Before writing or reviewing technical documentation, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md).
- Inspect the relevant files and nearby documentation. Keep each concept in its established location and link to its canonical explanation instead of duplicating it.
- For behavior and specification work, use the [semantic-spec workflow](skills/semantic-spec/SKILL.md) when its description matches the task or the user explicitly asks for it. Follow that workflow alongside these instructions.
- Keep changes within the requested scope. Before finishing, review the diff and remove unrelated edits.
