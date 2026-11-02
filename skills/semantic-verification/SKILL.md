---
name: semantic-verification
description: Select proportionate checks for specification coherence, examples, scenarios, compatibility, and semantic regressions.
disable-model-invocation: true
---

# Semantic verification

Use this workflow to check whether a specification is internally coherent and whether its examples, scenarios, tests, and implementation evidence support the claims being made. The repository-root `AGENTS.md` routes to this skill. This workflow supplements [`semantic-specification`](../semantic-specification/SKILL.md) and [`DOCUMENTATION_STANDARDS.md`](../../DOCUMENTATION_STANDARDS.md); it does not define behavior or make implementation observations authoritative semantics.

## Select checks by impact

Choose checks that can detect errors introduced by the change. This is a guide, not a mandatory checklist: omit irrelevant checks and explain material gaps when a useful check cannot be performed.

## Contract consistency

Inspect the affected canonical rules and their dependencies for:

- contradictions between definitions, requirements, conditions, exceptions, and transitions;
- undefined or inconsistently used terms;
- incompatible constraints or missing preconditions;
- qualifications that were lost or broadened;
- duplicated claims that can drift across prose, tables, examples, or transition descriptions.

Check both the changed section and the places that rely on it. Keep the canonical contract distinct from summaries, evidence, and implementation notes.

## Examples and explanatory material

Check that affected examples:

- illustrate the canonical rule and use defined terminology;
- show outcomes permitted by the contract;
- do not imply guarantees or restrictions absent from the contract;
- remain consistent with relevant tables, diagrams, and summaries.

Update or remove stale examples. Treat examples as non-normative unless the specification explicitly says otherwise. Do not use an example to silently settle an open question.

## Scenarios, boundaries, and transitions

Where behavior changes, examine representative scenarios selected for the affected contract. Depending on scope, these may include:

- valid and invalid inputs or operations;
- boundary conditions and relevant exceptions;
- state transitions, including their preconditions and observable results;
- interactions with adjacent rules that could change the outcome.

Add or update executable tests when a suitable test harness exists. Otherwise, record concise, reviewable scenarios with expected outcomes and the contract rule that supports each outcome.

## Compatibility and regression

When a change may affect prior behavior or guarantees:

- compare the changed contract with previously documented guarantees and representative scenarios;
- identify affected consumers or interactions where evidence permits;
- state whether migration, versioning, or a compatibility note is needed, or why it is not;
- preserve focused regression cases when practical.

If an expected result changes, explain whether this reflects an intentional contract change, an incorrect old test, or behavior that was previously unspecified. Do not change expected results merely to make a test pass.

## Implementation evidence

Report separately:

- what the specification requires;
- what the implementation currently does, if inspected;
- what relevant tests exercise and pass or fail;
- what remains unverified.

A passing test establishes only the behavior exercised by that test in the tested environment. Implementation structure, names, or current behavior do not by themselves prove the intended contract.

## Validation discipline

Run relevant available checks and inspect their results. If no executable check is suitable, perform a manual review of the selected scenarios and state that limitation. Do not claim tests were run, conformance was established, or behavior was verified unless the evidence supports that exact claim.

## Completion report

Summarize the contracts and scenarios examined, checks performed and their results, inconsistencies found or corrected, and material gaps or unverified claims. Keep the report proportionate to the change.
