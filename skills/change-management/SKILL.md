---
name: change-management
description: Classify proposed specification and documentation changes and determine proportionate decision and impact analysis.
disable-model-invocation: true
---

# Change management

Use this workflow for substantive changes to a specification, its guarantees, or the instructions governing specification work. It does not authorize the agent to make consequential semantic decisions for the user.

## Classify the change

Classify by effect on the documented contract, not by diff size or the author's label. A change may have multiple classifications.

- **Editorial:** wording or formatting changes without a change in meaning.
- **Clarification:** makes an existing contract easier to understand or apply.
- **Semantic:** changes specified behavior, constraints, guarantees, or observable outcomes.
- **Compatibility-affecting:** may invalidate a documented guarantee, consumer assumption, or interaction.
- **Structural:** reorganizes material without changing the contract.

A small wording change can be semantic. Do not classify every normative edit as semantic. If the effect is uncertain, explain why.

## Choose a proportionate process

1. Identify the canonical contract and the reason for the change.
2. Establish whether the change follows an accepted decision or requires a new one.
3. For semantic or compatibility-affecting changes, consider meaningful alternatives and consequences.
4. Ask the user only when materially different interpretations remain and the answer could affect behavior, guarantees, compatibility, or another consequential outcome.
5. Keep deferred decisions open. Update the contract only after the relevant decision is established.

Use the lightest process that protects the decision. Editorial and structural work does not need proposal ceremony without a concrete reason.

## Assess impact

Trace only consequences relevant to the change. Consider dependent rules, summaries, examples, tables, diagrams, links, compatibility assumptions, tests, implementation evidence, consumers, and migration needs.

Identify which canonical rules and dependent representations may be affected. This is impact scoping, not the editing or semantic-deduplication procedure; use [semantic-specification](../semantic-specification/SKILL.md) for that.

Keep intended contract, published claims, implementation behavior, test evidence, and unresolved questions distinct.

## Report

For substantive work, state the classification and rationale, decisions and open questions, material compatibility/downstream impact, canonical and dependent sections changed, and checks actually performed. Do not claim a decision, migration, test, or verification that did not occur.
