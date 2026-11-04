---
name: change-management
description: Classify proposed specification and documentation changes and determine proportionate decision and impact analysis.
disable-model-invocation: true
---

# Change management

Use this workflow when a task proposes or makes a substantive change to a specification, its guarantees, or the instructions governing specification work. Activate this skill only when the user explicitly requests it or an already activated project instruction links to it, as defined by the repository bootstrap contract. This workflow does not authorize an agent to make semantic decisions on the user's behalf.

## Classify the change

Classify by the effect on the documented contract, not by diff size or the author's description. A change may have more than one classification.

- **Editorial:** wording, formatting, or navigation changes that do not alter meaning.
- **Clarification:** makes an existing contract easier to understand or apply without changing its intended meaning.
- **Semantic:** adds, removes, or changes specified behavior, constraints, guarantees, or observable outcomes.
- **Compatibility-affecting:** may invalidate a previously documented guarantee, consumer assumption, interaction, or implementation.
- **Structural:** reorganizes material without changing the contract.

Do not label a change semantic merely because it touches normative prose. Conversely, a small wording change is semantic if it changes what the contract permits, requires, or guarantees. If the effect is uncertain, state what cannot yet be classified and why.

## Decide proportionate process

1. Identify the canonical contract and the reason for the proposed change.
2. Determine whether the change follows an existing accepted decision or requires a new decision.
3. For semantic or compatibility-affecting changes, identify meaningful alternatives and their consequences where relevant.
4. Ask the user only when materially different interpretations remain and the answer could affect behavior, guarantees, compatibility, or another consequential outcome.
5. Keep deferred decisions open. Do not turn an unresolved question into an implicit contract.
6. Update the canonical contract only after the relevant decision is established.

Editorial and structural changes should not acquire proposal ceremony without a concrete reason. Use the lightest process that protects the decision being made.

## Assess impact

Trace consequences in proportion to the change. Consider:

- dependent definitions, rules, preconditions, exceptions, and state transitions;
- summaries, tables, examples, diagrams, and cross-references that represent the changed contract;
- previously stated guarantees and compatibility assumptions;
- relevant tests, reference behavior, and implementation evidence;
- consumers, migration needs, or versioning implications when compatibility may change.

Identify which canonical rules and dependent representations may be affected; this is impact scoping, not the semantic-deduplication procedure. When the contract is being edited, use the search, ownership, and canonical-update procedure in [`semantic-specification`](../semantic-specification/SKILL.md). Do not expand the scope to unrelated areas merely to complete a checklist.

Keep distinct:
- the intended contract;
- published claims about that contract;
- observed implementation behavior;
- evidence from tests or other sources;
- unresolved questions.

## Decision status

Use status labels only when they help readers understand a consequential decision:

- **Proposed:** under consideration; not yet an accepted contract.
- **Accepted:** the relevant decision has been made.
- **Rejected:** considered and not adopted.
- **Deferred:** intentionally left unresolved.
- **Verified:** supporting checks or evidence have been examined for the stated scope.

Verification is independent of decision status: an accepted contract may remain unverified in an implementation. These labels describe the state of a decision or claim; they do not require a separate record for every change.

## Report

For substantive work, report briefly:

- the change classification and its rationale;
- decisions made and consequential questions left open;
- compatibility or downstream impact identified;
- canonical sections changed and dependent material aligned;
- checks performed and what they do—and do not—establish.

Do not claim a decision, migration, test, or verification that did not occur.
