---
name: semantic-spec
description: Iterative, user-led workflow for specifying system behavior and technical semantics.
disable-model-invocation: true
---

# Specification workflow

Use this workflow only when the user explicitly asks for the semantic-spec workflow. The repository router points here for that case.

Read [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md) for recurring documentation-quality criteria; this skill owns the semantic-spec workflow, not a second set of documentation standards.

## Steps

1. **Read context.** Inspect the target and relevant sources; identify existing decisions, conflicts, and each concept's canonical location.
2. **Find consequential questions.** Prioritize uncertainty that could change behavior, constraints, ownership, ordering, errors, or compatibility. Usually ask one focused question at a time; combine independent questions when useful.
3. **Resolve uncertainty.** Ask rather than guess when interpretations materially differ or assumptions could change the design. If the user defers, record the topic as open with its current scope and continue independent work. Do not ask follow-up questions that further subdivide a deferred topic unless the user reopens it or new evidence makes resolution necessary. If an answer conflicts with an earlier decision or source, explain the conflict and ask how to resolve it.
4. **Update the specification.** Record decisions and open questions where the concept belongs. Correct affected examples, summaries, and tables; do not append transcripts or duplicate definitions. Apply [Semantic deduplication](#semantic-deduplication) when changing or adding a rule.
5. **Check consequences.** Select only checks relevant to the behavior being specified:
   - For state-changing behavior, consider the starting state, trigger, relevant conditions, result, and failure behavior. Use an explicit state-transition model only when it helps clarify meaningful behavior.
   - Consider retries, delays, and concurrency when they could change outcomes or create conflicts or duplicate effects.
   - When multiple rules, events, sources, or updates can apply, clarify priority or order if it affects the outcome.
   - Distinguish actions that transfer responsibility, create an entity, change an existing entity, or only change a reference when that distinction matters.
   - Do not infer identical behavior from similar names alone.
   - Check for contradictions, missing dependencies, and consequential edge cases.
6. **Continue or wrap up.** Repeat as needed. Summarize decisions captured, consequential open questions and their impact, and remaining validation.

## Semantic deduplication

Treat duplication as a relationship between claims, not merely matching text. The same rule may be repeated with different wording, or represented in prose, a table, an example, and a transition description.

Before editing a concept or rule:

1. Search the relevant documentation for its terms, aliases, paraphrases, and other representations (including tables, examples, transition descriptions, and summaries).
2. Classify the occurrences: identify the canonical contract, necessary local context, derived consequences, evidence/history, and genuinely independent rules. Do not assume that similar wording always means the same rule.
3. Determine which document and section own the rule based on its scope and level of abstraction. If ownership is unclear or contested, resolve that before spreading the wording across documents.

When editing:

- Change the canonical contract first.
- At other occurrences, prefer a link to the canonical explanation. Retain only the minimum local statement needed to make a table, example, or section understandable on its own.
- Do not repeat the same qualification or caveat at every place that mentions the concept. Keep a qualification beside the rule it limits, and link to it where needed.
- Do not remove repetitions mechanically: retain context that changes the scope, actor, condition, consequence, or evidential status.

After editing:

1. Search again, including for paraphrases and equivalent claims rather than exact strings alone.
2. Compare the remaining occurrences for meaning, scope, conditions, actors, outcomes, and qualifications. Remove redundant restatements and correct stale summaries or contradictions.
3. Review the surrounding sections and affected documents, not just the edited paragraph, to catch duplicates that predate the change as well as ones introduced by it.

## Stage gates

- **Before editing:** choose a proportionate validation plan.
- **Before reporting completion:** run relevant available checks. State when a check cannot be run, and report only checks confirmed by results.

## Interaction rules

- Prioritize behavioral decisions over wording; reopen agreed decisions only when meaningful new evidence warrants it.
- In progress updates, distinguish **decisions accepted**, **edits pending**, **changes committed**, and **validation performed**. Claim a commit or passing check only when confirmed by tool results; link reported commits.

## Efficiency and decision discipline

- **Derive before asking:** apply agreed rules by analogy where their scope permits; ask only when materially different interpretations remain.
- **Separate semantics from evidence:** missing code or tests do not make an agreed semantic contract undecided. Mark unverified implementation behavior separately.
- **Research in batches:** read required instructions and canonical sources first. Inspect implementation to answer concrete evidence questions; search around explicit hypotheses and repeat only when new evidence warrants it.
- **Report at decision boundaries:** summarize changes, verification, and remaining questions at meaningful milestones without repeating unchanged findings.

## Commit discipline

- Keep accepted decisions and required edits in the working tree while pursuing independent specification work; do not commit after every answer.
- Commit when a coherent semantic block is complete, the user requests it, or substantial uncommitted work is at risk. A milestone alone is insufficient.
- Before committing, review the full accumulated diff for that block, confirm each edit follows accepted decisions or corrects an inconsistency without changing agreed semantics, and remove unrelated edits.
- Apply [Semantic deduplication](#semantic-deduplication) to changed concepts and their affected occurrences. Check that no open question was silently resolved.
- Prefer one coherent commit per semantic block. Do not rewrite existing history solely to reduce commit count.

## Ready for review

The specification is ready when:
- Goal and scope are clear.
- Important behavior can be checked against examples, tests, or acceptance criteria.
- Conflicts are resolved or recorded; consequential open questions and their impact remain visible.
- Definitions and links are consistent, with one canonical location per concept.
- Remaining evidence gathering and implementation validation are distinguished from semantic decisions.

If a criterion is unmet, state what remains and why; do not claim completion.
