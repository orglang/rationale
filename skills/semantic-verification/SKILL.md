---
name: semantic-verification
description: Select proportionate checks for specification coherence, examples, scenarios, compatibility, and semantic regressions.
disable-model-invocation: true
---

# Semantic verification

Use this workflow to check whether a specification is coherent and whether examples, scenarios, tests, and implementation evidence support its claims. It checks the result; it does not define behavior or make semantic decisions.

## Select proportionate checks

Choose checks that can detect errors introduced by the change. This is guidance, not a mandatory checklist. Omit irrelevant checks and explain material gaps.

### Contract consistency

Inspect the changed canonical rules and relevant dependencies for:
- contradictions between definitions, requirements, conditions, exceptions, and transitions;
- undefined or inconsistently used terms;
- lost or broadened qualifications and incompatible constraints;
- duplicate claims across prose, tables, examples, or transition descriptions.

Check the changed section and places that rely on it. Keep the canonical contract distinct from summaries, evidence, and implementation notes. Resolve substantive conflicts through [semantic-specification](../semantic-specification/SKILL.md).

### Examples and scenarios

Check that affected examples use defined terms, illustrate permitted outcomes, and do not imply unsupported guarantees. Update or remove stale examples. Treat examples as non-normative unless the specification says otherwise; do not use them to settle open questions silently.

When behavior changes, examine representative scenarios relevant to the affected contract: inputs, boundaries, exceptions, transitions, and adjacent rules where applicable. Add executable tests when a suitable harness exists; otherwise record concise expected outcomes and the rules supporting them.

### Compatibility and regression

When prior behavior or guarantees may be affected:
- compare the new contract with documented guarantees and representative scenarios;
- identify affected consumers where evidence permits;
- state whether migration, versioning, or a compatibility note is needed, or why not;
- preserve focused regression cases when practical.

If an expected result changes, explain whether the contract intentionally changed, the old test was incorrect, or the behavior was previously unspecified.

### Implementation evidence

Report separately what the specification requires, what implementation behavior was inspected, what relevant tests exercise and their results, and what remains unverified. A passing test establishes only the behavior it exercises in the tested environment. Names, structure, or current implementation behavior do not by themselves prove intended semantics.

## Validation and report

Run relevant available checks and inspect their results. If no executable check is suitable, perform a manual review and state that limitation. Do not claim conformance or verification beyond the evidence.

Summarize the contract and scenarios examined, checks and results, inconsistencies found or corrected, and material gaps. Keep the report proportionate to the change.
