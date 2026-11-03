# Agent instructions

Use this file as the repository-wide router. Keep detailed rules in their canonical module and follow the pointer for the task at hand.

## Documentation

Before writing or reviewing technical documentation or agent instructions, read [`DOCUMENTATION_STANDARDS.md`](DOCUMENTATION_STANDARDS.md). It owns recurring documentation-quality criteria.

When the user explicitly asks to use the semantic-specification workflow for system behavior, domain rules, protocols, requirements, or technical semantics, follow [`skills/semantic-specification/SKILL.md`](skills/semantic-specification/SKILL.md). Do not activate that workflow for routine proofreading or documentation-only edits.

The reading order is this router, the applicable general standards, and then the task-specific workflow. References from those lower-level documents back to this file identify ownership and routing; they do not require restarting the reading order.

For classification and impact analysis of substantive changes, see [`skills/change-management/SKILL.md`](skills/change-management/SKILL.md).

For checks of specification coherence, behavior scenarios, and semantic regressions, see [`skills/semantic-verification/SKILL.md`](skills/semantic-verification/SKILL.md).

For manual behavioral evaluation of repository agent workflows, when explicitly requested, use [`skills/behavior-evaluation/SKILL.md`](skills/behavior-evaluation/SKILL.md).

## Responsibility boundaries

- **Documentation standards** own repository-wide quality principles: canonical-source discipline, evidence distinctions, terminology, clarity, and review criteria.
- **Change management** owns change classification, decision-process proportionality, and downstream impact assessment.
- **Semantic specification** owns semantic decisions and the operational workflow for finding and resolving duplicate claims while updating the canonical contract.
- **Semantic verification** owns independent checks of the resulting contract, scenarios, regressions, and implementation evidence.

A workflow may point to another module's responsibility, but should not restate that module's procedure. Keep completion reports distinct: report the decisions and contract edits, the change classification and impact, or the checks and results according to the workflow that owns that work.

## Changes and review

Keep edits targeted. Before finishing or committing, review the full diff against the branch base and remove accidental or unrelated changes.

## Retrospectives

For each `#retro` note, add a separate top-level comment to the relevant pull request as soon as the note arises. Do not wait until the retrospective ends, combine notes into one comment, or use commit messages to store them.

When the user starts a retrospective, group the recorded notes, compare them with evidence, and decide what to accept, reject, or defer. Notes do not authorize repository changes; agree on the scope of instruction changes before editing them. Prefer correcting an existing instruction that failed to guide behavior over adding a duplicate rule. Keep retrospective notes scoped to the current conversation unless the user asks otherwise.
