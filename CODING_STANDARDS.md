# Documentation review standards

These standards guide human and agent review of research documentation. They complement `AGENTS.md`: keep task-specific workflow instructions there, and use this file for recurring editorial judgment.

## Semantic accuracy

- Define a term before relying on it, or link to its canonical definition at first use.
- Keep one canonical explanation for each concept. In glossaries, tables, summaries, and open-question lists, prefer a concise summary plus a cross-reference over a second full definition.
- Separate intended language semantics from publication claims and implementation observations. Code structure or field names alone do not establish language semantics.
- Label uncertainty explicitly. Do not silently turn a hypothesis into a fact or smooth over disagreements between sources.
- Distinguish the status of a claim from implementation coverage. Apply status labels to specific claims, not to a term as a whole.

## Structure and readability

- Give each section a clear purpose. Keep detailed explanations in the section that owns the concept and point back to it elsewhere.
- Make tables useful for comparison rather than using them for long prose. Split, simplify, or replace wide tables when their meaning becomes difficult to follow on a narrow screen.
- Introduce abbreviations, symbols, and field names before using them in reasoning; explain whether a name is a language term, publication notation, or implementation identifier.
- Keep headings, status labels, terminology, and cross-reference style consistent throughout the document.

## Evidence and references

- For substantial or disputed claims, record the claim, source, status, and any mismatch or limitation. Keep straightforward glossary entries lightweight.
- Prefer direct source links and precise section references. Check that internal links and heading anchors point to the intended target.
- State what the evidence establishes and what remains unverified. Avoid implying that a source was inspected or a behavior tested when it was not.

## Final review

Before committing a documentation change:

1. Search for all mentions of the affected concept and update its canonical explanation first.
2. Check for duplicated definitions, terms used before explanation, inconsistent labels, and contradictory caveats.
3. Review tables and long lists for scanability, especially on narrow screens.
4. Verify changed links and cross-references, and ensure examples match the surrounding explanation.
5. Remove caveats that repeat the same point; preserve caveats that mark a real uncertainty or evidence boundary.
6. Confirm that the diff changes only the intended files and that the final wording does not claim more than the available evidence supports.

These are review criteria, not all mechanically enforceable lint rules. Use automated checks for deterministic formatting and link failures; use editorial review for semantic accuracy and clarity.
