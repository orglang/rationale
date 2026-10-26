# Agent instructions

Use these instructions repository-wide; linked documents own detailed review criteria and task-specific workflows.

## Changes and review

- Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.

## Retrospectives

- Accumulate `#retro` notes during work and include them in the next suitable commit message. Keep notes scoped to the current conversation unless the user asks otherwise.
- When the user starts a retrospective, group notes, compare them with evidence, and decide what to accept, reject, or defer. Notes do not authorize repository changes.

## Technical documentation

- Before writing or reviewing technical documentation, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md). Inspect relevant files and nearby documentation; keep each concept in its canonical location and link to it rather than duplicating it.
- When the user explicitly asks to use the semantic-spec workflow for system behavior, domain rules, protocols, requirements, or technical semantics, follow [`skills/semantic-spec/SKILL.md`](skills/semantic-spec/SKILL.md).

## Agent instructions

- When creating or refactoring agent-facing instructions, skills, their invocation descriptions, or instruction routing, follow [`skills/writing-instructions/SKILL.md`](skills/writing-instructions/SKILL.md).
