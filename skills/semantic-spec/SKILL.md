---
name: semantic-spec
description: Collaboratively develop a precise technical specification by resolving semantic decisions one at a time, keeping agreed decisions and open questions explicit, and updating the canonical document as understanding evolves. Use when defining or revising system behavior, requirements, protocols, domain rules, state transitions, or technical semantics.
---

# Semantic Spec

Turn an incomplete problem description into a precise, reviewable technical specification through a focused dialogue. Optimize for shared understanding and correct semantics, not document length.

## Workflow

1. **Establish the current state.** Read the existing specification and relevant project context before proposing changes. Identify the goal, known constraints, decisions already made, contradictions, and highest-impact unknowns. Preserve valid existing decisions.
2. **Choose one decision.** Ask one focused question about the highest-impact unresolved issue. Prefer questions whose answer changes behavior, boundaries, invariants, ownership, ordering, failure handling, or compatibility. Give brief options and explain trade-offs only when they help the user decide.
3. **Resolve meaning.** Interpret the answer in context. If it is ambiguous, ask a targeted follow-up instead of silently choosing an interpretation. Treat a clear deferral as an open question, not a decision. When the answer conflicts with an earlier decision, surface the conflict and ask which should prevail.
4. **Update the specification.** After each meaningful answer, update the canonical document or provide the exact revised section if no writable document is available. Record the decision in its proper place; avoid appending an unstructured transcript. Keep terminology consistent and make implications explicit.
5. **Validate.** Check the updated text for contradictions, undefined terms, hidden assumptions, missing failure cases, and behavior that cannot be tested. If validation reveals a consequential unresolved choice, return to step 2 with one question.
6. **Continue or conclude.** Repeat until the user asks to stop or the completion criteria below are met. Summarize the decisions made, remaining open questions, and consequential risks.

## Evidence and uncertainty

- Distinguish explicitly between confirmed decisions, facts from source material, inferences, proposals, and unresolved questions.
- Never present an inference or proposal as user-approved behavior.
- Keep deferred questions visible with their impact where known; do not block unrelated progress on them.
- Ask the user to resolve consequential ambiguity; use a clearly labeled, reversible assumption only when progress is otherwise impossible and the risk is low.
- Do not ask again about a decision already settled unless new information creates a real conflict.

## Writing rules

- Specify observable behavior and outcomes, not vague intentions.
- Define important terms before relying on them.
- Describe state changes using preconditions, trigger, resulting state, and failure behavior where applicable.
- State ownership, ordering, invariants, boundaries, and error behavior when relevant to the system.
- Prefer concrete examples and counterexamples when they disambiguate semantics.
- Keep each decision in one canonical location. Link or refer to it elsewhere rather than duplicating it.
- Separate normative requirements from rationale, examples, and implementation suggestions.
- Use the project's existing format and terminology unless there is a clear reason to change them.

For a deeper checklist of semantic distinctions, consult [SEMANTIC-RULES.md](SEMANTIC-RULES.md) when the task involves domain modeling, state transitions, ownership, ordering, or uncertainty that needs careful treatment.

## Completion criteria

The specification is ready for review when:

- The goal, scope, actors, and important terms are defined.
- Agreed behavior is distinguishable from assumptions and open questions.
- Important flows, state transitions, boundaries, and failure cases are described where applicable.
- Requirements are concrete enough to verify with examples, tests, or explicit acceptance criteria.
- No known contradictions remain undisclosed.
- Remaining open questions are listed with their impact, rather than silently resolved.
- The document is internally consistent and uses one source of truth for each decision.

Do not claim the specification is complete if any criterion is unmet; describe what remains and why.
