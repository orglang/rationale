---
name: semantic-specification
description: Iterative, user-led workflow for specifying system behavior and technical semantics.
---

# Specification workflow

Use this workflow to define, change, or resolve system behavior, domain rules, protocols, requirements, or technical semantics. Routine proofreading and documentation-only edits do not activate it. Derive consequences from accepted decisions; do not make consequential semantic decisions on the user's behalf.

## Workflow

1. **Understand the current model.** Read the target, relevant sources, and existing decisions. Identify conflicts, uncertainties, and canonical ownership. Do not infer semantics from names or implementation structure alone.
2. **Resolve consequential ambiguity.** Derive what follows from agreed decisions and apply agreed rules by analogy where appropriate. Ask only when materially different interpretations remain and cannot be resolved from available decisions or evidence. If the user defers a question, keep it open and continue independent work.
3. **Choose the right level of detail.** Specify enough to make the contract coherent and checkable. Do not turn every unspecified edge case or implementation choice into a question or rule. Stop when more detail would not change meaning or how it can be checked.
4. **Update the canonical contract.** Put each decision or open question where the concept belongs. Change its canonical explanation first, then align only affected dependent material. Do not append conversation transcripts or silently resolve open questions.
5. **Trace consequences.** Examine adjacent rules and operational details only when they could materially affect the agreed behavior. Distinguish semantic analysis from independent verification and implementation evidence.
6. **Review and report.** Review the relevant diff for contradictions, duplication, stale examples, broken links, and unrelated edits. Run proportionate checks and report decisions, open questions, changes, and actual validation.

For substantive changes, use [change-management](../change-management/SKILL.md) to classify the request and assess impact. Use [semantic-verification](../semantic-verification/SKILL.md) to check the result independently.

## Semantic ownership and deduplication

This section owns the editing procedure. Other workflows may identify scope or check the result, but should not repeat this procedure.

- Before editing, search relevant documents for the concept, aliases, paraphrases, and other representations. Identify the canonical contract and distinguish it from local context, derived consequences, evidence, and independent rules.
- Keep each normative rule in one canonical location. Elsewhere use a link or the minimum local explanation needed. A mention of a concept is not automatically a duplicate claim.
- Update dependent material only when it makes a claim that becomes inaccurate, conflicts with the new contract, or must change to preserve its own meaning. Do not propagate wording mechanically to every occurrence or incidental mention.
- Retain text that changes scope, actor, condition, consequence, or evidential status. Keep qualifications beside the rule they limit.
- After editing, search again for equivalent claims. Remove redundant restatements and correct stale summaries or contradictions in affected sections.
- If ownership is unclear or contested, resolve it before propagating the change.

## Working discipline

Keep semantic decisions separate from evidence. Missing code or tests do not make an accepted contract undecided; mark implementation behavior separately. Accumulate related edits, inspect the full diff before committing, and prefer one coherent commit per semantic block. Do not claim a commit or passing check until confirmed.

## Ready for review

The specification is ready when its scope is clear, important behavior is checkable, consequential conflicts and open questions are visible, definitions and links are consistent, and remaining evidence gaps are explicit.
