# Documentation review standards

These criteria govern research and technical documentation. [`AGENTS.md`](AGENTS.md) routes repository-wide work; [`skills/semantic-spec/SKILL.md`](skills/semantic-spec/SKILL.md) owns the user-led semantic-spec workflow. This file owns recurring documentation-quality criteria.

## Accuracy and evidence

- Define terms before use. Keep each substantive definition and rule in one canonical location; elsewhere provide only the local context needed and link to that source. Keep necessary brief repetitions subordinate and consistent.
- Distinguish intended behavior, published claims, and implementation observations. Code structure or field names alone do not establish semantics.
- Treat user-confirmed contracts as intended behavior, not proof of formal semantics, unless authoritative sources support that claim.
- Mark uncertainty and disagreement. Keep claim status separate from implementation coverage; apply status labels to claims, not terms.
- For important or disputed claims, identify the specific sources, confidence/status, limitations, what the evidence establishes, and what remains unverified. Name the source, test, or decision needed rather than making vague appeals to authority or generic requests for evidence. Never imply a source was inspected or behavior tested when it was not.
- Distinguish behavior that is intentionally inapplicable from behavior that remains undefined. Record an open question when that distinction could affect behavior.
- For each consequential open question, state what is unknown, which behavior or decision it affects, and what evidence, test, or person could resolve it. Prefer questions whose answers distinguish meaningful outcomes; do not invent states or add boilerplate for completeness.

## Structure and language

- Give each section a clear purpose and keep details with the section that owns them. Use links to canonical explanations rather than duplicating them.
- Use readable tables for comparisons, especially on narrow screens. Define abbreviations and symbols before use; clarify whether a name is a language term, document notation, or implementation identifier.
- Keep headings, terminology, status labels, and cross-references consistent. State behavior, the identity of the entity or resource involved, the boundaries of its scope, and ownership directly; use contrasts only when they clarify a real distinction.
- Preserve qualifications that affect meaning.
- Describe the current model and rationale, not the history of how wording or a document evolved. Include history only when it explains a current decision, compatibility constraint, or unresolved question.
- Use negative formulations when they prevent a plausible misunderstanding or define a meaningful boundary. Avoid repeated statements of what does not happen when one precise positive statement or a single scoped caveat is enough.

## References and final review

- Prefer direct source links and precise section references. Verify changed links, heading anchors, and examples.
- Search for affected concepts elsewhere. Update the canonical explanation first, then correct inaccurate summaries and examples.
- Check for duplicate definitions, undefined terms, inconsistent labels, contradictions, and repetitive caveats. Preserve caveats that express real uncertainty or evidence limits.
- Check that each sentence adds a fact, attributed claim, evidence, limitation, open question, or useful navigation; remove repetition and unhelpful links.
- Ensure the diff contains only relevant changes and claims no more than the evidence supports.

These are review criteria, not a required template. Automate repeatable checks when possible; review meaning, evidence, and clarity manually.
