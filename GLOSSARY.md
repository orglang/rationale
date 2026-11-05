# OrgLang glossary

> **Status: informative shared vocabulary.** This glossary collects concepts used across the OrgLang research documents. It summarizes common terminology but does not introduce or replace language rules. Domain-specific terms are defined in their owning specifications, which remain authoritative for their grammar, semantics, and constraints.

## Execution and model entities

| Term | Definition | Canonical reference |
|---|---|---|
| **Incarnation** | One concrete runtime instance of an executing entity, with its own execution state and local namespace. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Participant** | A pool or process incarnation taking part in a communication or protocol interaction. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships); [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Pool** | A participant that makes capabilities available to other pools and may service process incarnations under agreements. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Process** | A named computational entity; context distinguishes its declaration and definition from a running incarnation. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Identifier** | A name or reference to a runtime resource; distinct from a syntactic placeholder. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Placeholder** | A syntactic name whose runtime referent is supplied by substitution; it is not the resource itself. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Term** | An abstract expression describing an action or computation. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Value** | An item communicated through a channel and interpreted according to the applicable value grammar. | [Incarnations and channels, §5](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Continuation** | An expression that becomes eligible for execution after the interaction that enables it. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |

## Channels and communication

| Term | Definition | Canonical reference |
|---|---|---|
| **Channel** | A communication resource with an identity and two endpoints. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Endpoint** | One participant-relative end of a shared channel. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Channel identity** | The identifier of a channel resource, distinct from a placeholder or incarnation identifier. | [Incarnations and channels, §2–3](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Pending interaction** | A publication or subscription awaiting its corresponding peer action; it is not yet a completed interaction. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Matching** | The point at which corresponding endpoint actions meet and establish the shared interaction effect specified by the applicable protocol. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Residual protocol state** | The portion of a protocol that remains after the interaction steps already performed. | [Pools and transaction types](about-pools-and-transaction-types/README.md); [Processes and session types](about-processes-and-session-types/README.md) |
