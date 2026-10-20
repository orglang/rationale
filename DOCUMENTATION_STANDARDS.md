# Documentation review standards

Use these criteria when writing or reviewing research and technical documentation. [`AGENTS.md`](AGENTS.md) contains repository-wide instructions; [`skills/semantic-spec/SKILL.md`](skills/semantic-spec/SKILL.md) defines the workflow for resolving consequential behavior and specification decisions. This file owns recurring documentation quality criteria.

## Accuracy and evidence

- Define a term before relying on it, or link to its canonical definition at first use. Explain each concept in one place; elsewhere, summarize briefly and link back.
- Distinguish intended behavior, claims from published sources, and implementation observations. Code structure or field names alone do not establish language semantics.
- Treat a user-confirmed contract as the agreed direction of the document, not proof of formal language semantics. Label it as intended behavior unless an authoritative language source supports a stronger claim.
- Mark uncertainty and disagreement explicitly. Distinguish the status of a claim from implementation coverage; apply status labels to individual claims, not terms as a whole.
- For important or disputed claims, identify the source, status or confidence, and relevant limitations. State what the evidence establishes and what remains unverified. Never imply that a source was inspected or behavior tested when it was not.

## Structure and language

- Give each section a clear purpose and keep details in the section that owns the concept.
- Use tables for comparisons, not long prose. Split or simplify tables that are hard to scan on narrow screens.
- Define abbreviations and symbols before use. Clarify whether a name is a language term, document notation, or implementation identifier.
- Keep headings, terminology, status labels, and cross-reference style consistent.
- Describe behavior, scope, and ownership directly. Use contrasts only when they clarify a real distinction; preserve qualifications that affect meaning.
- Replace vague appeals to authority or generic calls for more evidence with the specific source, test, or decision needed.

## References and final review

- Prefer direct source links and precise section references. Verify changed links, heading anchors, and examples.
- Search for other mentions of affected concepts. Update the canonical explanation first, then correct summaries or examples that have become inaccurate.
- Check for duplicate definitions, undefined terms, inconsistent labels, contradictions, and caveats that repeat the same point. Preserve caveats that mark real uncertainty or evidence limits.
- Read each sentence in context: it should add a fact, attributed claim, evidence, limitation, open question, or useful navigation. Remove repetition and links that do not help readers.
- Confirm the diff contains only relevant changes and that the wording does not claim more than the evidence supports.

These are review criteria, not a required template. Automate repeatable checks when repository tools or CI support them; review meaning, evidence, and clarity manually.
