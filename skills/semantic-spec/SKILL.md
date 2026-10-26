---
name: semantic-spec
description: Guide iterative, user-led specification of system behavior, domain rules, protocols, requirements, and technical semantics by resolving consequential decisions and updating the canonical document. Do not use for routine proofreading or documentation-only edits.
---

# Specification workflow

Activate this workflow only when the user explicitly asks to use it. Do not activate it automatically because a task matches this description or repository instructions refer to it.

Read [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md) for documentation quality and use the checks below as a selective review aid, not a required template.

## Steps

1. **Read context.** Inspect the target and relevant sources; identify existing decisions, conflicts, and each concept's canonical location.
2. **Find consequential questions.** Prioritize uncertainty that could change behavior, constraints, ownership, ordering, errors, or compatibility. Usually ask one focused question at a time; combine independent questions when useful.
3. **Resolve uncertainty.** Ask rather than guess when interpretations materially differ or assumptions could change the design. If the user defers, record the topic as open with its current scope and continue independent work. Do not ask follow-up questions that further subdivide a deferred topic unless the user reopens it or new evidence makes resolution necessary. If an answer conflicts with an earlier decision or source, explain the conflict and ask how to resolve it.
4. **Update the specification.** Record decisions and open questions where the concept belongs. Correct affected examples, summaries, and tables; do not append transcripts or duplicate definitions. Keep edits, decisions, and commits distinct; follow [Commit discipline](#commit-discipline).
5. **Check consequences.** Select only checks relevant to the behavior being specified:
   - For state-changing behavior, consider the starting state, trigger, relevant conditions, result, and failure behavior. Use an explicit state-transition model only when it helps clarify meaningful behavior.
   - Consider retries, delays, and concurrency when they could change outcomes or create conflicts or duplicate effects.
   - When multiple rules, events, sources, or updates can apply, clarify priority or order if it affects the outcome.
   - Distinguish actions that transfer responsibility, create an entity, change an existing entity, or only change a reference when that distinction matters.
   - Do not infer identical behavior from similar names alone.
   - Check for contradictions, missing dependencies, and consequential edge cases.
6. **Continue or wrap up.** Repeat as needed. Summarize decisions captured, consequential open questions and their impact, and remaining validation.

## Stage gates

- **Before editing:** choose a proportionate validation plan.
- **Before reporting completion:** run relevant available checks. State when a check cannot be run, and report only checks confirmed by results.

## Interaction rules

- Prioritize behavioral decisions over wording; reopen agreed decisions only when meaningful new evidence warrants it.
- Preserve existing structure, terminology, status labels, and section ownership. Do not create parallel standards or taxonomies.
- In progress updates, distinguish **decisions accepted**, **edits pending**, **changes committed**, and **validation performed**. Claim a commit or passing check only when confirmed by tool results; link reported commits.

## Efficiency and decision discipline

- **Derive before asking:** apply agreed rules by analogy where their scope permits; ask only when materially different interpretations remain.
- **Separate semantics from evidence:** missing code or tests do not make an agreed semantic contract undecided. Mark unverified implementation behavior separately.
- **Research in batches:** read required instructions and canonical sources first. Inspect implementation to answer concrete evidence questions; search around explicit hypotheses and repeat only when new evidence warrants it.
- **Report at decision boundaries:** summarize changes, verification, and remaining questions at meaningful milestones without repeating unchanged findings.

## Commit discipline

- Keep accepted decisions and required edits in the working tree while pursuing independent specification work; do not commit after every answer.
- Commit when a coherent semantic block is complete, the user requests it, or substantial uncommitted work is at risk. A milestone alone is insufficient.
- Before committing, review the full accumulated diff for that block, check canonical ownership and cross-references, remove unrelated edits, and ensure changes follow accepted decisions or correct inconsistencies without changing agreed semantics.
- Search for other occurrences of each changed concept; update the canonical contract first, then align affected summaries, examples, tables, and cross-references. Confirm that no open question was silently resolved.
- Prefer one coherent commit per semantic block. Do not rewrite existing history solely to reduce commit count.

## Ready for review

The specification is ready when:
- Goal and scope are clear.
- Important behavior can be checked against examples, tests, or acceptance criteria.
- Conflicts are resolved or recorded; consequential open questions and their impact remain visible.
- Definitions and links are consistent, with one canonical location per concept.
- Remaining evidence gathering and implementation validation are distinguished from semantic decisions.

If a criterion is unmet, state what remains and why; do not claim completion.
