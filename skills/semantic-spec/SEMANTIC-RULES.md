# Checklist for defining behavior

Use this checklist during specification work. [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md) covers documentation quality; [`SKILL.md`](SKILL.md) covers the workflow.

Select only questions that could affect the behavior. This is a review aid, not a complete formal model or required template.

## Behavior and boundaries

For each relevant concept or operation, consider:

- **Scope and identity:** Which entity or resource is involved, and what bounds its scope (e.g. user, organization, transaction, time window, trust boundary, or API version)?
- **Preconditions:** What must be true before the behavior is allowed?
- **Roles and permissions:** Who initiates, owns, views or changes the resource, approves the action, or is accountable? Can these roles differ?
- **Trigger and rules:** What starts the behavior, and which validation, permission, condition, or precedence rule applies?
- **Outcome:** What state changes, and what can an external observer see?
- **Errors and rejection:** What happens when a prerequisite is missing, processing fails, or a request is rejected?
- **Retries and concurrency:** Can the operation repeat, be delayed or retried, or run concurrently? What determines the result?

Distinguish behavior that does not apply from behavior that remains undefined. Record an open question when that distinction could affect behavior.

## State transitions

For state-changing behavior, describe the starting state, trigger, relevant conditions, result, and failure behavior. Specify ordering, retries, and concurrency only when they affect the outcome. Examples clarify rules; they do not replace them.

## Interacting rules

When multiple rules, events, sources, or updates can apply, define their priority or order if it affects the outcome. Clarify whether an action transfers responsibility, creates an entity, changes an existing entity, or only changes a reference. Similar names do not imply identical behavior.

## Open questions

For each consequential open question, record:
- what is unknown;
- which behavior or decision it affects;
- what evidence, test, or person could resolve it.

Prefer questions whose answers distinguish meaningful outcomes. Do not invent states or add boilerplate for completeness; add other questions when the system requires them.
