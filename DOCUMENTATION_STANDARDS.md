# Documentation standards

These standards apply to research and technical documentation. Task-specific procedures belong to the relevant workflow.

## Accuracy and evidence

- Define terms before use. Keep each substantive definition and normative rule in one canonical location; elsewhere provide necessary local context and link to the source.
- Distinguish intended behavior, published claims, implementation observations, and test evidence. Names or code structure alone do not establish semantics.
- Treat user-confirmed contracts as intended behavior, not proof of formal semantics unless authoritative sources support that claim.
- Mark uncertainty and disagreement. Keep claim status separate from implementation coverage; apply status labels to claims, not terms.
- For important or disputed claims, identify the specific sources, confidence/status, limitations, what the evidence establishes, and what remains unverified. Name the source, test, or decision needed rather than making vague appeals to authority. Never imply that a source was inspected or behavior tested when it was not.
- Distinguish intentionally inapplicable behavior from undefined behavior when that distinction affects outcomes. For each consequential open question, state what is unknown, which behavior or decision it affects, and what evidence, test, or person could resolve it. Prefer questions whose answers distinguish meaningful outcomes; do not invent states or add boilerplate for completeness.

## Structure and language

- Give each section a clear purpose. Put details with the section that owns them; use links instead of duplicating explanations.
- Keep terminology, headings, status labels, and cross-references consistent. State behavior, the identity of the entity or resource involved, scope, conditions, and ownership directly; distinguish language terms, document notation, and implementation identifiers where ambiguity is possible.
- Describe the current contract and rationale, not the history of how wording evolved. Do not frame current behavior merely as a transition from, or negation of, a previous version when a direct statement is possible. Retain history only when it explains a current decision, compatibility constraint, or unresolved question.
- Use negative formulations when they define a meaningful boundary or prevent a plausible misunderstanding; avoid repetitive negatives when one precise statement is enough.
- Preserve qualifications that affect meaning. Use readable tables for comparisons and define abbreviations before use.

## References and review

- Prefer direct source links and precise section references. Verify changed links, anchors, and examples.
- Search for affected concepts. Update the canonical explanation first; then correct dependent summaries, examples, and contradictions. Do not rewrite incidental mentions that do not make a normative claim or depend on the changed rule.
- Check for duplicate definitions, stale examples, undefined terms, inconsistent labels, and unhelpful repetition.
- Keep changes within scope and ensure every sentence adds useful information, evidence, a limitation, or navigation.

These are review criteria, not a mandatory template or a requirement to run every check on every task.
