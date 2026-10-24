# Documentation review standards

These criteria govern research and technical documentation. [`AGENTS.md`](AGENTS.md) owns repository-wide instructions; [`SKILL.md`](skills/semantic-spec/SKILL.md) owns the semantic-spec workflow. This file owns recurring documentation quality criteria.

## Accuracy and evidence

- Define terms before use or link to their canonical definition. Explain each concept once; summarize and link elsewhere.
- Distinguish intended behavior, published claims, and implementation observations. Code structure or field names alone do not establish semantics.
- Treat user-confirmed contracts as intended behavior, not proof of formal semantics, unless authoritative sources support that claim.
- Mark uncertainty and disagreement. Keep claim status separate from implementation coverage; apply status labels to claims, not terms.
- For important or disputed claims, identify sources, confidence/status, limitations, what the evidence establishes, and what remains unverified. Never imply a source was inspected or behavior tested when it was not.

## Structure and language

- Give each section a clear purpose; keep details with the section that owns them and use links instead of duplicate explanations.
- Use readable tables for comparisons, especially on narrow screens. Define abbreviations and symbols before use; clarify whether a name is a language term, document notation, or implementation identifier.
- Keep headings, terminology, status labels, and cross-references consistent. State behavior, scope, and ownership directly; use contrasts only when they clarify a real distinction.
- Replace vague appeals to authority or generic requests for evidence with the specific source, test, or decision needed. Preserve qualifications that affect meaning.

## References and final review

- Prefer direct source links and precise section references. Verify changed links, heading anchors, and examples.
- Search for affected concepts elsewhere. Update the canonical explanation first, then correct inaccurate summaries and examples.
- Check for duplicate definitions, undefined terms, inconsistent labels, contradictions, and repetitive caveats. Preserve caveats that express real uncertainty or evidence limits.
- Each sentence should add a fact, attributed claim, evidence, limitation, open question, or useful navigation. Remove repetition and unhelpful links.
- Ensure the diff contains only relevant changes and claims no more than the evidence supports.

These are review criteria, not a required template. Automate repeatable checks when possible; review meaning, evidence, and clarity manually.
