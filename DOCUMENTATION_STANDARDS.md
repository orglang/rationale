# Documentation review standards

These standards describe how to review research and technical documentation. They complement `AGENTS.md`, which contains repository-wide instructions. Specialized skills may explain when and how to apply these standards, but should not redefine them.

## Semantic accuracy

- Define a term before relying on it, or link to its canonical definition at first use.
- Keep one canonical explanation for each concept. In glossaries, tables, summaries, and open-question lists, prefer a concise summary plus a cross-reference over a second full definition.
- Separate intended language semantics from publication claims and implementation observations. Code structure or field names alone do not establish language semantics.
- A contract confirmed by the user records the agreed direction of the document; it does not, by itself, establish formal language semantics. Label it as intended behavior until an authoritative language source supports a stronger claim.
- Label uncertainty explicitly. Do not silently turn a hypothesis into a fact or smooth over disagreements between sources.
- Distinguish the status of a claim from implementation coverage. Apply status labels to specific claims, not to a term as a whole.

## Structure and readability

- Give each section a clear purpose. Explain each concept in one place and link to that explanation elsewhere.
- Use tables for comparisons, not long passages of prose. Split or simplify wide tables that are hard to read on narrow screens.
- Define abbreviations and symbols before using them. Clarify whether a name is a language term, notation used in the document, or an identifier from the implementation.
- Keep headings, status labels, terminology, and cross-reference style consistent throughout the document.
- Describe behavior, scope, and ownership directly. Use contrasts only when they clarify a real difference; keep qualifications that affect the meaning.
- Remove process commentary, vague appeals to authority, and generic reminders to gather evidence. For unresolved claims, name the source or test needed to verify them.
- Check every sentence for a clear purpose: a technical fact, attributed claim, evidence, limitation, open question, or useful link. Remove sentences that add nothing, and check adjacent sentences for repetition.

## Evidence and references

- For important or disputed claims, record the claim, source, confidence or status, and any limitation or disagreement. Keep simple glossary entries brief.
- Prefer direct source links and precise section references. Check that internal links and heading anchors point to the intended target.
- State what the evidence establishes and what remains unverified. Avoid implying that a source was inspected or a behavior tested when it was not.

## Final review

Before submitting a documentation change:

1. Search for other mentions of the affected concept and update its main explanation first.
2. Look for duplicate definitions, undefined terms, inconsistent labels, and conflicting qualifications.
3. Check that tables and long lists are easy to scan, especially on narrow screens.
4. Verify changed links and cross-references, and ensure examples match the surrounding explanation.
5. Remove caveats that repeat the same point; preserve caveats that mark a real uncertainty or evidence boundary.
6. Confirm that only relevant files changed and that the wording does not claim more than the evidence supports.
7. Remove repeated claims and adjacent links that do not help readers navigate.

These standards are review guidance, not a required template or a replacement for task instructions. Automate repeatable checks when the repository provides a tool or CI job; review meaning, evidence, and clarity manually.
