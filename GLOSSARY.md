# OrgLang glossary

> **Status: informative shared vocabulary.** This glossary collects concepts used across the OrgLang research documents. It summarizes common terminology but does not introduce or replace language rules. Domain-specific terms are defined in their owning specifications, which remain authoritative for their grammar, semantics, and constraints.

**Typography:** a shared term is bolded where it is first substantively introduced or defined in a document. Later occurrences are plain unless emphasis is needed for another reason. Boldface identifies vocabulary; it does not make a statement normative.

## Execution and model entities

| Term | Definition | Canonical reference |
|---|---|---|
| **Incarnation** | One concrete runtime instance of an executing entity, with its own execution state and local namespace. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Execution state** | The runtime state maintained by an incarnation while it executes. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Participant** | A pool or process incarnation taking part in a communication or transaction interaction. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships); [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Pool** | A participant that makes capabilities available to other pools and may service process incarnations under agreements. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Process** | A named computational entity; context distinguishes its declaration and definition from a running incarnation. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Term declaration** | A declaration that gives a named process's interface, including its channel parameters. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Term definition** | A definition that gives the body or expression specifying a named process's behavior. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Identifier** | A name or reference to a runtime resource; distinct from a syntactic placeholder. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Placeholder** | A syntactic name whose runtime referent is supplied by substitution; it is not the resource itself. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Substitution** | Replacement of a placeholder in a term by an identifier, according to the applicable binding discipline. | [Incarnations and channels, §6](about-incarnations-and-channels/README.md#6-substitution-and-continuation-application) |
| **Term** | An abstract expression describing an action or computation. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Value** | An item communicated through a channel and interpreted according to the applicable value grammar. | [Incarnations and channels, §5](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Continuation** | A continuation associated with a term or a type; its specific meaning depends on the layer of the model. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Term continuation** | A continuation that selects or supplies the next term after a value is matched and applied. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Process continuation** | A process expression that becomes eligible for execution after the interaction that enables it. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Calls and spawns, §1](about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls) |
| **Type continuation** | The residual type expression that describes the interactions permitted after the current interaction, including any refinements that constrain the runtime states or values admitted at that point. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |

## Channels and communication

| Term | Definition | Canonical reference |
|---|---|---|
| **Channel** | A communication resource with an identity and two endpoints. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Endpoint** | One participant-relative end of a shared channel. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Provider endpoint** | The endpoint from which a participant provides the service or initiates the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Client endpoint** | The complementary endpoint from which a participant uses the service or takes part in the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Channel identity** | The identifier of a channel resource, distinct from a placeholder or incarnation identifier. | [Incarnations and channels, §2–3](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Public channel** | A channel exposed as the public interaction point for a participant; in the pool model, the public transaction channel is the stable access point when no private access is active. | [Pools and transaction types, §5](about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel) |
| **Private channel** | A channel used for a private access associated with a logical transaction channel; in the pool model it has a distinct physical identity and carries the access-local allocation state. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md) |
| **Publication** | An endpoint action that makes a value available on a channel for a matching subscription. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Subscription** | An endpoint action that waits on a channel for a matching publication and supplies a continuation for the received value. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Pending interaction** | A publication or subscription awaiting its corresponding peer action; it is not yet a completed interaction. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Matching** | The point at which corresponding endpoint actions meet and establish the shared interaction effect specified by the applicable type. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Agreement** | The committed allocation state (the value of `Q`) associated with a logical transaction channel and accepted by the participating pools. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement) |
| **Protocol type** | A type that specifies, from the provider endpoint's perspective, the interactions permitted over a channel, the complementary actions expected from the client endpoint, and the continuations permitted after those interactions. Session types and transaction types are distinct specializations; the category does not imply shared syntax or identical state semantics. | [Processes and session types, §6](about-processes-and-session-types/README.md); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Session type** | A protocol type that describes the interactions permitted over a channel, expressed from the provider endpoint's point of view. | [Processes and session types, §6](about-processes-and-session-types/README.md) |
| **Transaction type** | A protocol type that describes the transaction interactions permitted through a pool's transaction channel, including their continuations and applicable allocation-state changes. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Constraint** | A condition restricting the states or values for which a type or interaction is permitted. | [Incarnations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Refinement** | A restriction attached to a type expression that narrows the states or values it admits. | [Incarnations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Linearity** | A channel usage and ownership discipline that prevents channel endpoints or bindings from being duplicated or silently discarded. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |

