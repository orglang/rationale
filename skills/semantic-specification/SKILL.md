---
name: semantic-specification
description: Iterative, user-led workflow for specifying system behavior and technical semantics.
disable-model-invocation: true
---

# Specification workflow

Use this workflow only when the user explicitly asks for it. This skill owns the user-led semantic workflow.

## Workflow

1. **Understand the current model.** Read the target, relevant sources, and existing decisions. Identify conflicts, uncertainties, and the canonical location of each affected concept. Do not infer semantics from names or implementation structure alone.
2. **Resolve consequential ambiguity.** First derive consequences from the agreed model and apply agreed rules by analogy where their scope permits. Ask only when materially different interpretations remain and cannot be resolved from the agreed decisions or available evidence, and the answer could change behavior, guarantees, compatibility, or another consequential part of the model. Otherwise, record the uncertainty at the appropriate level and continue independent work. If the user defers a question, keep it open and continue independent work.
3. **Keep the right level of abstraction.** Work at the level of detail needed to make the contract coherent and checkable. Do not turn every unspecified detail, edge case, or possible implementation choice into a question or a new rule. Derive what follows from the current model; leave details that do not affect its meaning open or out of scope. Stop refining a point when further detail would not change the contract, its consequences, or how it can be checked.
4. **Update the canonical contract.** Put each decision or open question where the concept belongs. Change its canonical explanation first, then align affected summaries, examples, tables, and links. Do not append conversation transcripts or silently resolve open questions.
5. **Reason through relevant consequences.** Trace consequences far enough to understand whether a proposed decision changes the contract or its dependent rules. Examine edge cases or operational details only when they could materially affect that behavior; this is not a checklist to expand every topic. This is semantic analysis, not an independent validation pass. Distinguish intended semantics from published claims and implementation evidence.
6. **Review and report.** Review the full relevant diff. Check for semantic duplication, contradictions, stale examples, broken links, and unrelated edits. Run proportionate available checks. Report decisions, open questions and their impact, changes actually made, and validation actually performed.

## Related workflows

For substantive changes, use [`change-management`](../change-management/SKILL.md) to classify the change and assess its impact.

Use [`semantic-verification`](../semantic-verification/SKILL.md) to select proportionate checks for affected behavior and possible semantic regressions.

## Semantic deduplication

This section owns the operational procedure for semantic deduplication. Other workflows may identify affected scope or check the resulting specification, but they do not repeat this procedure.

Treat duplication as repeated claims, not just repeated wording. A rule may recur as prose, a table row, an example, or a transition description.

- Before editing, search relevant documents for the concept, its aliases, paraphrases, and other representations. Identify the canonical contract and distinguish it from necessary local context, derived consequences, evidence, and independent rules.
- Keep the rule in one canonical location. Elsewhere use a link, or the minimum local explanation needed to understand that section.
- Keep qualifications beside the rule they limit; do not repeat the same caveat at every mention.
- Do not remove repetitions mechanically: retain text that changes scope, actor, condition, consequence, or evidential status.
- After editing, search again for paraphrases and equivalent claims. Remove redundant restatements and correct stale summaries or contradictions, including pre-existing duplicates in affected sections.

If ownership of a rule is unclear or contested, resolve that before propagating it across documents.

## Working discipline

- Keep semantic decisions separate from evidence: missing code or tests do not make an agreed contract undecided; mark unverified implementation behavior separately.
- Keep accepted decisions and related edits together while pursuing independent work. Do not commit after every answer.
- Before committing, inspect the full accumulated diff for the coherent change, confirm it follows accepted decisions, and remove unrelated edits. Prefer one coherent commit per semantic block; do not rewrite history merely to reduce commit count.
- Do not claim a commit or passing check until tool results confirm.

## Ready for review

The specification is ready when its goal and scope are clear, important behavior is checkable, conflicts and consequential open questions are visible, definitions and links are consistent, and remaining evidence or implementation validation is distinguished from semantic decisions.
