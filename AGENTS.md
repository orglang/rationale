# Agent instructions

Use this file as the repository-wide router. Keep detailed rules in their canonical module and follow the pointer for the task at hand.

## Documentation

Before writing or reviewing technical documentation or agent instructions, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md). It owns recurring documentation-quality criteria.

When the user explicitly asks to specify system behavior, domain rules, protocols, requirements, or technical semantics, follow [`skills/semantic-spec/SKILL.md`](skills/semantic-spec/SKILL.md). Do not activate that workflow for routine proofreading or documentation-only edits.

## Changes and review

Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.

## Retrospectives

Accumulate `#retro` notes during work and add them to the existing retrospective comment in the relevant pull request; do not use commit messages as a store for retrospective notes.

When the user starts a retrospective, group notes, compare them with evidence, and decide what to accept, reject, or defer. Notes do not authorize repository changes; agree on the scope of instruction changes before editing them. Prefer correcting an existing instruction that failed to guide behavior over adding a duplicate rule. Keep retrospective notes scoped to the current conversation unless the user asks otherwise.
