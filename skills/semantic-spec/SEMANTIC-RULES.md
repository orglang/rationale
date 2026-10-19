# Semantic rules reference

Use this reference when a specification needs more than a simple list of requirements. Apply only the sections relevant to the system; do not turn every section into mandatory boilerplate.

## Label the status of claims

Keep these categories distinct:

- **Confirmed** — explicitly decided by the user or an authoritative project source.
- **Source fact** — stated in existing documentation, code, contracts, or another named source.
- **Inference** — a conclusion derived from available facts; state the reasoning when consequential.
- **Proposal** — a suggested design that still needs approval.
- **Open** — not decided, deferred, or ambiguous.

If sources disagree, record the conflict and identify which authority must resolve it. Do not silently promote an inference or proposal to a confirmed requirement.

## Model behavior, not just nouns

For each important concept, clarify the distinctions that change behavior: identity, lifecycle, ownership, scope, constraints, and relationship to other concepts. Introduce a term only when it helps describe a meaningful domain distinction.

## Describe state transitions

When state matters, specify the relevant parts of this transition:

- **Current state / preconditions:** what must already be true.
- **Trigger:** what event or action initiates the change, and who or what initiates it.
- **Decision rule:** guards, validation, authorization, and precedence.
- **Result:** the new state and externally observable effects.
- **Failure or rejection:** what happens if a guard fails, processing fails, or the request is repeated.
- **Concurrency / repetition:** whether duplicate, delayed, or competing operations are possible and how they are handled.

Do not invent states or transitions merely to fill a template. Include only what the system requires.

## Make boundaries explicit

Clarify relevant boundaries such as tenant, user, organization, resource, transaction, time window, trust zone, or API version. State where a rule applies and where it does not. Avoid relying on a broad term like “global” without naming its scope.

## Specify ownership and authority

Distinguish who creates, owns, may view, may change, approves, or is accountable for an entity. Do not infer that access implies ownership, or that the actor initiating an action is the authority that approves it.

## Specify ordering and precedence

When multiple rules, events, sources, or updates can apply, define their precedence or ordering if it changes the result. If order is intentionally irrelevant, say so when that is important. Surface tie cases and conflicts rather than leaving them implicit.

## Make requirements verifiable

Prefer a statement that can be checked against a concrete example. Where helpful, include:
- a normal case;
- a boundary case;
- an invalid or forbidden case;
- a failure or retry case.

Use examples to clarify a rule, not to replace the rule itself. Do not imply that a short example list is exhaustive unless it is intended to be.

## Keep uncertainty actionable

For each consequential open question, record:
- what is unknown;
- which behavior or decision it affects;
- what information or authority could resolve it.

Do not let deferred questions disappear into prose. Avoid asking about low-impact details before the decisions that shape the architecture or semantics.
