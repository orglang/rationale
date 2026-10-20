# Checklist for defining behavior

Use this checklist to identify important details when defining system behavior. For evidence, terminology, links, and writing quality, follow [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md). The workflow in [`SKILL.md`](SKILL.md) explains how to use this checklist during a specification task.

Use only the questions that matter for the behavior being specified. This checklist is not a complete formal model or a required document template.

## Behavior and boundaries

For each concept or operation, ask which details can change observable behavior:

- **Scope and identity:** which entity or resource is involved, and what limits its scope (for example, user, organization, transaction, time window, trust boundary, or API version)?
- **Preconditions:** what must already be true for the behavior to be allowed?
- **Roles and permissions:** who initiates the action, owns the resource, can view or change it, approves it, or is accountable for it? These roles may differ.
- **Trigger and rules:** what starts the behavior, and which validation, permission, condition, or precedence rule applies?
- **Outcome:** what state changes, and what can an external observer see?
- **Errors and rejection:** what happens if a prerequisite is missing, processing fails, or the request is rejected?
- **Retries and concurrency:** can an operation be repeated, delayed, retried, or run at the same time as another? If so, what determines the outcome?

Include only relevant questions. Distinguish between something that does not apply and behavior that has not yet been defined. If the difference could affect behavior, record it as an open question.

## State transitions

When behavior changes state, describe the starting state, trigger, conditions, result, and failure behavior as needed. Specify ordering, retries, or concurrent behavior when they affect the result. Use examples to clarify ambiguity, not as a substitute for the rule.

## Interacting rules

When multiple rules, events, sources, or updates can apply, explain their priority or order if it affects the outcome. Clarify whether an action transfers responsibility, creates a new entity, changes an existing one, or only changes a reference. Similar names do not mean the behavior is the same.

## Actionable open questions

For each important open question, state:
- what is unknown;
- which behavior or design decision it affects;
- what evidence, test, or person can resolve it.

Ask questions that distinguish meaningfully different outcomes. Do not invent states or add boilerplate just to make a section look complete. Add other questions when the system needs them; do not add categories merely to complete the checklist.
