---
name: language-specification
description: Design, write, audit, and evolve technical documentation for programming and domain-specific languages. Use when creating or editing a language specification, grammar, syntax/semantics reference, type-system rules, standard-library/API reference, conformance requirements, examples, or documentation for Rationale.
---

# Language specification

Produce a specification that lets an independent implementer determine what a program means and whether an implementation conforms. Treat the document as an executable contract, not an overview or tutorial.

## Workflow

1. **Establish the source of truth.** Inspect the repository structure, existing docs, examples, tests, parser/lexer, implementation, and open design decisions. Prefer repository evidence over assumptions. Record conflicts between implementation and prose; do not silently choose one.
2. **Define the scope.** Identify the audience, implementation stage, language version, normative sections, and out-of-scope behavior. Separate current behavior from proposals and unresolved decisions.
3. **Build a concept map.** Trace the path from source text through lexical analysis, parsing, name resolution, typing, evaluation or compilation, runtime behavior, errors, and interoperability. Include only stages that exist in this language.
4. **Specify behavior before polishing prose.** For each feature, define syntax, constraints, meaning, edge cases, failure behavior, and interactions with other features. State observable behavior precisely.
5. **Validate every claim.** Compare rules with code and tests where available. Run relevant checks or examples if tools permit. Never claim tests passed unless they were actually run.
6. **Review adversarially.** Look for ambiguity, contradictions, missing cases, accidental implementation assumptions, and behavior that two independent implementers could reasonably interpret differently.
7. **Prune.** Remove repetition and background material that does not change an implementer's understanding or decision. Keep rationale and tutorials separate from normative rules.
8. **Report completion.** Summarize files changed, decisions made, checks run and their results, unresolved questions, and any implementation/specification mismatches.

## Normative language

Use **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** consistently, with their ordinary standards-document meanings. Use normative terms only for requirements. Explain a term if its meaning is intentionally different.

Distinguish explicitly between:
- **Normative rule:** required language or implementation behavior.
- **Informative explanation:** motivation, intuition, or non-binding guidance.
- **Example:** an illustration of a rule, not a substitute for the rule.
- **Open question:** behavior not yet decided; never present it as settled.

Avoid vague words such as “usually”, “naturally”, “simple”, “obvious”, “appropriate”, or “as expected” when they affect semantics. Replace them with explicit conditions and outcomes.

## Specify each language feature

For every syntax or semantic feature, answer the applicable questions below. Do not force irrelevant headings into small features; do not omit a question that affects observable behavior.

### Syntax and grammar
- Show the concrete syntax and a minimal valid example.
- Define terminals, nonterminals, precedence, associativity, and ambiguity where relevant.
- State whitespace, comments, line endings, delimiters, escaping, and tokenization rules where relevant.
- Use one consistent grammar notation and define its conventions.
- Explain how the grammar composes with neighboring productions; avoid isolated productions that cannot be interpreted in context.
- Distinguish syntax errors from later validation errors.

### Static semantics
- Define name lookup, scope, declaration order, shadowing, imports, and visibility where applicable.
- State type rules, inference, coercion, subtyping, overload resolution, and constraints explicitly.
- Give preconditions and postconditions for well-formed programs.
- Define compile-time restrictions separately from runtime behavior.

### Dynamic semantics
- Define evaluation order, effects, state changes, control flow, and observable results.
- Specify values, environments, storage, lifetime, and mutation where applicable.
- State error, exception, panic, cancellation, and termination behavior.
- Do not leave evaluation order or side effects implicit if programs can distinguish the alternatives.

### Interactions and boundaries
- Check interactions with scoping, types, modules, control flow, errors, serialization, and other relevant features.
- Cover boundary cases: empty input, missing values, duplicate declarations, overflow, invalid encodings, recursive definitions, and malformed programs where applicable.
- State implementation-defined, unspecified, and undefined behavior distinctly. Prefer eliminating these categories when the language design can do so.
- For implementation-defined behavior, require the implementation to document its choice. For unspecified behavior, enumerate permitted outcomes where practical. Do not use “undefined” as a synonym for “not yet designed”.

## Examples as tests

Examples are evidence, not decoration.

- Include the smallest example that demonstrates the rule, plus a counterexample when a nearby invalid form is easy to confuse with it.
- Label examples as valid, invalid, illustrative, or version-specific when that is not obvious.
- For each example, state the expected parse, type, output, error, or other observable result.
- Keep examples consistent with the normative text and with each other.
- Prefer examples that distinguish competing interpretations and expose edge cases.
- When the repository has executable examples or conformance tests, link them or run them instead of duplicating large snippets.
- Never invent output or imply an example was executed when it was not.

## Structure and terminology

Organize the document so readers can find rules by feature and implementers can follow dependencies. A useful default order is:

1. Status, scope, version, and conformance.
2. Design overview and terminology.
3. Source text and lexical structure.
4. Grammar and syntax.
5. Name resolution and static semantics.
6. Evaluation or execution semantics.
7. Modules, built-ins, and standard library.
8. Errors and diagnostics.
9. Interoperability and implementation requirements.
10. Conformance examples and appendices.

Adapt this order to the actual language; do not create empty sections just to match the outline.

Maintain a single canonical definition for each term and rule. Use stable terminology and identifiers. If a concept is renamed, update references and examples instead of leaving synonyms scattered across the specification. Link to the canonical rule rather than copying it.

Separate the following document types when their purposes differ:
- **Specification:** normative behavior and conformance.
- **Tutorial:** a guided learning path.
- **Reference:** searchable details for users.
- **Design note / ADR:** rationale, alternatives, and historical decisions.
- **Implementation notes:** current architecture and known limitations.

## Change control and versioning

When editing an existing specification:
- Preserve established behavior unless the task explicitly changes it.
- Identify whether a change is editorial, clarifying, additive, breaking, or unresolved.
- For semantic changes, document compatibility impact, migration implications, and affected examples/tests.
- Keep version-specific rules explicit; do not silently rewrite historical semantics.
- If the implementation disagrees with the specification, report the mismatch and ask or document which source should govern rather than silently changing either side.
- Update cross-references, glossary entries, examples, and conformance tests alongside the rule.

## Review checklist

Before calling the work complete, verify:

- [ ] Every normative requirement is testable or has an observable interpretation.
- [ ] Syntax and semantics agree; grammar notation is defined and consistent.
- [ ] Evaluation order and error behavior are explicit wherever observable.
- [ ] Terms have one meaning and are used consistently.
- [ ] Examples have expected outcomes and match the rules.
- [ ] Relevant interactions and boundary cases are covered.
- [ ] Normative rules are distinguishable from rationale and examples.
- [ ] Cross-references, version labels, and links are valid.
- [ ] No claim about implementation or test results is unsupported.
- [ ] Open questions and known mismatches are listed rather than hidden.
- [ ] Repeated or non-operative prose has been removed.

## Completion criteria

The task is complete only when the requested document changes are made, relevant checks have been run where possible, and the final report separates verified facts from assumptions. If a decision is required from the language designer, present the smallest concrete question with the competing options and their consequences; do not fabricate a decision to make the document look finished.
