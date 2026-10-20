# Checklist for defining behavior

Use this checklist during a specification task. For documentation quality, follow [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md); for the workflow, see [`SKILL.md`](SKILL.md).

Select only the questions that could affect the behavior being specified. This is a review aid, not a complete formal model or a required template.

## Behavior and boundaries

For each relevant concept or operation, consider:

- **Scope and identity:** Which entity or resource is involved, and what limits its scope (for example, user, organization, transaction, time window, trust boundary, or API version)?
- **Preconditions:** What must be true before the behavior is allowed?
- **Roles and permissions:** Who initiates the action, owns the resource, can view or change it, approves it, or is accountable for it? Can these roles differ?
- **Trigger and rules:** What starts the behavior? Which validation, permission, condition, or precedence rule applies?
- **Outcome:** What state changes, and what can an external observer see?
- **Errors and rejection:** What happens if a prerequisite is missing, processing fails, or a request is rejected?
- **Retries and concurrency:** Can the operation be repeated, delayed, retried, or run concurrently? What determines the outcome?

Distinguish behavior that does not apply from behavior that is not yet defined. If that distinction could affect behavior, record an open question.

## State transitions

When behavior changes state, describe the starting state, trigger, relevant conditions, result, and failure behavior. Specify ordering, retries, and concurrent behavior only when they affect the outcome. Use examples to clarify the rule, not replace it.

## Interacting rules

When multiple rules, events, sources, or updates can apply, state their priority or order if it affects the outcome. Clarify whether an action transfers responsibility, creates an entity, changes an existing entity, or only changes a reference. Similar names do not imply identical behavior.

## Open questions

For each consequential open question, record:
- what is unknown;
- which behavior or design decision it affects;
- what evidence, test, or person could resolve it.

Prefer questions whose answers distinguish meaningfully different outcomes. Do not invent states or add boilerplate to make a section look complete. Add other questions when the system requires them.
