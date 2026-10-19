---
name: semantic-spec
description: Facilitate iterative, user-guided development of a technical specification by choosing the next consequential semantic decision, resolving ambiguity, updating the canonical document, and repeating. Use when a user is defining or revising system behavior, domain rules, protocols, requirements, or technical semantics—not for routine proofreading or documentation-only edits.
---

# Semantic Spec

Use this workflow to turn an incomplete model into a reviewable specification. The skill defines the collaboration loop; repository documentation standards define the quality bar for the resulting text.

## Workflow

1. **Load project rules and context.** Read the repository's agent instructions and documentation standards first (in this repository: `AGENTS.md` and `CODING_STANDARDS.md`). Inspect the target document, its directory, canonical concept owners, and relevant cross-references. Preserve established decisions and document boundaries.
2. **Find the next consequential decision.** Identify unresolved choices that affect observable behavior, invariants, scope, ownership, ordering, failure handling, or compatibility. Ask one focused question about the highest-impact choice. Offer options only when they clarify real alternatives.
3. **Resolve the answer.** If the answer is ambiguous, ask a targeted follow-up rather than guessing. If the user defers the decision, keep it open and continue with independent work. If it conflicts with an earlier decision or source, surface the conflict and ask which authority should resolve it.
4. **Update the canonical document.** After each meaningful answer, edit the section that owns the concept, or provide the exact replacement text if direct editing is unavailable. Update dependent references only where needed; do not append a conversation transcript or duplicate the canonical definition.
5. **Check semantic consequences.** Verify that the answer fits the existing model and does not introduce contradictions, undefined dependencies, or unhandled boundary behavior. Consult [SEMANTIC-RULES.md](SEMANTIC-RULES.md) for the relevant modeling checklist. Apply the repository's documentation standards for evidence, terminology, structure, and review.
6. **Repeat or conclude.** Continue with one question at a time until the user stops or the completion criteria below are met. On conclusion, summarize decisions captured, unresolved questions and their impact, and any remaining validation work.

## Interaction rules

- Prioritize decisions that change system behavior over wording or low-impact details.
- Do not ask again about a settled decision unless new evidence creates a meaningful conflict.
- Make assumptions explicit and reversible; ask before relying on an assumption that could materially change the design.
- Keep deferred questions visible without blocking unrelated progress.
- Treat implementation observations, publication claims, and intended language behavior according to the repository's evidence policy; do not infer normative semantics from code structure alone.
- Use the existing document structure, terminology, status vocabulary, and ownership boundaries. Do not create a new parallel standard or status taxonomy.

## Completion criteria

The specification is ready for review when:

- The goal and scope of the behavior being specified are clear.
- Consequential behavior and constraints are described precisely enough to review against examples, tests, or acceptance criteria.
- Known conflicts are resolved or explicitly recorded.
- Open questions that could change the design remain visible with their impact.
- Canonical definitions and cross-references are consistent with the repository's document ownership.
- Remaining evidence or implementation validation is clearly distinguished from semantic decisions.

Do not claim completion while a criterion is unmet; state what remains and why.
