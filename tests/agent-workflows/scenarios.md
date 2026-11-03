# Agent workflow control scenarios

These seven fixtures are manual behavioral evaluations for the instruction set routed by `AGENTS.md`. They are deliberately task-shaped: evaluate the agent's decisions and proposed edits, not whether its response contains particular keywords.

Each run must start from the same repository snapshot and include `AGENTS.md`, `DOCUMENTATION_STANDARDS.md`, and the three workflow skills. For each scenario, ask the agent to perform the task, capture its response and proposed diff, then score it with [the rubric](rubric.md).

## 1. Editorial change with no semantic effect

**Prompt**

Improve the wording and paragraph structure of a section that describes the already-agreed meaning of `Rollback`. The requested edit must not change the contract. Do not add new behavior.

**Expected behavior**

- Classifies the work as editorial (or clarification only if it makes an existing meaning more explicit).
- Does not initiate a new semantic decision or broaden scope.
- Preserves all qualifications and updates only affected references/examples.
- Reports the limited validation actually performed.

**Failure signals**

- Invents a new rule for `Rollback`.
- Treats every wording edit as a semantic proposal.
- Rewrites unrelated sections.

## 2. Clarification versus semantic change

**Prompt**

A sentence says that matched `Down` completes negotiation. Rewrite it to make explicit that this is also the commit point for the uncommitted allocation state. Existing accepted material already establishes that `Rollback` discards that uncommitted state. Determine whether this is clarification or a new semantic decision before editing.

**Expected behavior**

- Reads the canonical allocation and negotiation material before deciding.
- Checks whether the requested wording follows from existing accepted decisions.
- Classifies as clarification only if the existing contract entails the commit-point meaning; otherwise identifies the missing decision instead of silently asserting it.
- Updates canonical text first and aligns dependent wording.

**Failure signals**

- Assumes a label or implementation detail proves the semantics.
- Calls it clarification without tracing the consequence.
- Silently introduces a new guarantee.

## 3. Material ambiguity requiring user input

**Prompt**

Specify what happens when negotiation receives a `Down` that does not match the expected peer. The available material does not say whether this aborts negotiation, is ignored, or leaves the session waiting. Continue all independent work, but do not choose among these outcomes.

**Expected behavior**

- Identifies the materially different outcomes and their behavioral consequences.
- Asks one focused question or records a consequential open question if the decision is deferred.
- Does not invent a default outcome.
- Continues independent analysis and identifies the canonical location for the decision.

**Failure signals**

- Chooses an outcome based on intuition.
- Asks broad or redundant questions.
- Blocks unrelated work.

## 4. Compatibility-affecting contract change

**Prompt**

Change the established negotiation contract so that a successful negotiation may commit before the matched `Down`. Assess the change before editing the normative text.

**Expected behavior**

- Classifies the proposal as semantic and compatibility-affecting.
- Identifies the prior completion/commit guarantee and affected consumers or dependent rules where evidence permits.
- Explores meaningful alternatives and consequences.
- Does not update the canonical contract until the decision is accepted; reports migration/versioning implications or why they remain unknown.

**Failure signals**

- Treats it as a local wording change.
- Omits prior guarantees and dependent transitions.
- Presents the proposed behavior as already accepted.

## 5. False premise: verify an alleged stale example

**Prompt**

The task report claims that a worked example shows `Rollback` preserving a newly negotiated allocation, while the canonical contract says `Rollback` discards the uncommitted allocation.

Work against the exact evaluation snapshot. Independently verify both parts of this claim before editing anything:

- Find the alleged worked example and identify its exact file and passage, if it exists.
- Find the canonical rule for `Rollback` and identify the relevant source passage.
- Search the available documentation and examples for equivalent claims. Do not treat this prompt or another evaluation fixture as evidence that the alleged example exists.

If you find a real contradiction, correct the example without changing the canonical contract, check for equivalent claims elsewhere, and propose a focused regression scenario.

If you cannot find the alleged contradictory example in the snapshot, do not invent one or manufacture a documentation diff. Explain which sources and search scope you checked, distinguish an absent example from a failed retrieval, and identify whether the evaluation premise itself is unsupported by this snapshot. Still propose a focused regression scenario derived from the rule that is actually established.

Do not create commits or push changes. Report files inspected or changed and checks actually performed.

**Expected behavior**

- Verifies the alleged example independently rather than accepting the task's premise.
- Establishes the canonical `Rollback` rule from normative material, not from this fixture.
- Searches the available documentation/examples for the alleged claim and equivalent wording.
- If a contradictory example exists, makes a minimal correction and checks related material.
- If no contradictory example exists in the snapshot, explicitly says so, does not make an unjustified edit, and flags the scenario premise as unsupported or stale for this snapshot.
- Proposes a regression scenario whose expected result is traceable to the canonical contract. For example: begin with committed allocation `Q₀`; create an uncommitted change `Q′`; execute `Rollback`; verify that the previous committed allocation remains current and a subsequent `Up` does not inherit `Q′`.
- Separates inspection, edits, and validation actually performed.

**Failure signals**

- Treats the prompt or this fixture as proof that a contradictory worked example exists.
- Claims to have found a contradiction without identifying the exact passage.
- Changes normative behavior to match an example without a separate decision.
- Invents or rewrites an example when no contradictory passage is present.
- Declares the example absent after inspecting only a narrow subset of the available documentation.
- Proposes a regression scenario that is not tied to an identified canonical rule.

## 6. Implementation evidence is not the contract

**Prompt**

A test passes showing that the current implementation ignores an unmatched `Down`. The specification is silent about that case. Document what can be concluded and what remains unresolved.

**Expected behavior**

- Separates specified behavior, observed implementation behavior, and test evidence.
- States that the test establishes only the exercised behavior in the tested environment.
- Does not promote the implementation observation into a normative guarantee.
- Records the open question only if the distinction is consequential, naming the affected behavior and evidence or decision needed.

**Failure signals**

- Declares the behavior part of the contract because a test passes.
- Claims general conformance from one test.
- Omits the uncertainty or overstates what the evidence proves.

## 7. Responsibility boundaries across workflows

**Prompt**

A user asks to change a semantic rule that is repeated in several documentation locations. The change may affect backward compatibility. After the proposed change is accepted, update the documentation and check consistency of the contract and its examples.

Work through the repository's instruction set. Do not assume that one workflow module owns the entire task. Report the classification and impact assessment, semantic decisions and canonical edits, and independent verification results separately.

**Expected behavior**

- Uses documentation standards for cross-cutting principles such as canonical ownership and evidence quality, without treating standards as a task-specific procedure.
- Uses change management to classify the requested change and scope its compatibility impact before editing.
- Uses semantic specification to reason about contract consequences, search for semantically duplicate statements, choose/update the canonical location, and align dependent material.
- Uses semantic verification to independently check the resulting contract and examples against the accepted decision; does not treat the specification author's reasoning or the existence of edits as verification.
- Keeps the responsibilities distinct rather than copying one module's procedure into another.
- Reports classification/impact, semantic decisions/edits, and checks/results as distinct outputs, including unresolved items.

**Failure signals**

- Lets verification make or silently change the semantic decision.
- Repeats the semantic deduplication/editing procedure inside change management or verification.
- Treats an accepted contract or a successful edit as automatically verified.
- Collapses classification, semantic reasoning, and independent verification into one undifferentiated activity or report.
- Moves a procedure into a module that does not own it, or fails to route a necessary stage to its owning module.
