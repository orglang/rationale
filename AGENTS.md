# Agent instructions

Use these instructions repository-wide; linked documents own detailed review criteria and task-specific workflows.

## Changes and review

- Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.

## Retrospectives

- Accumulate `#retro` notes during work and add them to the existing retrospective comment in the relevant pull request; do not use commit messages as a store for retrospective notes.
- When the user starts a retrospective, group notes, compare them with evidence, and decide what to accept, reject, or defer. Notes do not authorize repository changes; agree on the scope of instruction changes before editing them.
- Prefer correcting an existing instruction that failed to guide behavior over adding a duplicate rule. Keep retrospective notes scoped to the current conversation unless the user asks otherwise.

## Technical documentation

- Before writing or reviewing technical documentation, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md). Inspect relevant files and nearby documentation; keep each concept in its canonical location and link to it rather than duplicating it.
- When the user explicitly asks to use the semantic-spec workflow for system behavior, domain rules, protocols, requirements, or technical semantics, follow [`skills/semantic-spec/SKILL.md`](skills/semantic-spec/SKILL.md).
