# Semantic modeling checklist

This file supplements the repository's documentation standards. For evidence labels, source attribution, terminology, canonical definitions, links, and final editorial review, follow the repository's `CODING_STANDARDS.md`; do not redefine those policies here.

Apply only the modeling prompts relevant to the concept being specified. Do not force every specification into a fixed template.

## Behavior and boundaries

For each concept or operation whose semantics matter, ask which distinctions change observable behavior:

- **Scope and identity:** what entity or resource is involved, and within what boundary (for example, user, organization, transaction, time window, trust zone, or API version)?
- **Preconditions:** what must already be true for the behavior to be allowed?
- **Authority and ownership:** who initiates, owns, may inspect or modify, approves, or is accountable for the entity or transition? Do not assume these roles are identical.
- **Trigger and decision rule:** what event initiates the behavior, and which validation, authorization, guard, or precedence rule applies?
- **Result:** what state changes and externally observable effects follow?
- **Failure and rejection:** what happens when a precondition fails, processing fails, or the request is rejected?
- **Repetition and concurrency:** can operations be duplicated, delayed, retried, or race? If so, what determines the outcome?

Include only the dimensions relevant to the system. If a dimension is intentionally unspecified, record it as an open question when that omission affects behavior.

## State transitions

When a behavior changes state, describe the relevant parts of the transition: starting state, trigger, guard or decision rule, resulting state, and failure behavior. Include ordering, retry, or concurrency semantics when they affect the result. Use a concrete example or counterexample to expose an ambiguity, but do not let examples replace the rule.

## Interacting rules

When multiple rules, events, sources, or updates may apply, specify precedence or ordering if it changes the outcome. Clarify whether an action transfers responsibility, creates a new entity, mutates an existing one, or merely changes a reference. Similar names do not establish equivalent behavior.

## Actionable open questions

For each consequential unresolved choice, make clear:
- what is unknown;
- which behavior or design decision it affects;
- what evidence, test, or decision-maker could resolve it.

Prefer questions that separate materially different outcomes. Do not fill gaps with invented states or boilerplate simply to make a section look complete.
