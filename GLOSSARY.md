# OrgLang glossary

> **Status: informative terminology reference.** This glossary records shared vocabulary used across the OrgLang research documents. It summarizes concepts but does not introduce or replace language rules. Linked canonical documents remain authoritative for detailed definitions, constraints, and lifecycle rules.

Implementation identifiers are not model terms. Their observed correspondence to model concepts belongs in the implementation-mapping sections of the specifications that own the relevant behavior.

## Execution and names

| Term | Definition | Canonical reference |
|---|---|---|
| **Incarnation** | One concrete runtime instance of an executing entity, with its own execution state and local namespace. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Participant** | A pool or process incarnation taking part in a channel interaction. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships); [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Identifier** | A name or reference to a runtime resource; distinct from a syntactic placeholder. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Placeholder** | A syntactic name whose runtime referent is supplied by substitution; it is not the resource itself. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Term** | An abstract expression describing an action or computation. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Value** | An item published through a channel and interpreted according to the domain-specific value grammar. | [Incarnations and channels, §5](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Continuation** | An expression that becomes eligible after a matching communication and value application. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Pool** | A participant that communicates with other pools and may service a process incarnation under an agreement. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Pool term** | An executable expression describing a pool's communication or state transition. | [Pools and transaction types, §3](about-pools-and-transaction-types/README.md#3-pool-model) |
| **Process** | A named computational entity; context distinguishes its declaration/definition from a running incarnation. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Named process** | A process identified by a name, with a declaration and definition. | [Processes and session types, §2, §4](about-processes-and-session-types/README.md#2-core-concepts) |
| **Process declaration** | The interface of a named process, including its channel parameters. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Process definition** | The body or expression specifying the behavior of a named process. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Process incarnation** | One concrete running instance of a process. The current model assigns each incarnation a never-reused identity. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Servicing pool** | The pool associated with a process incarnation and responsible for servicing its provider channel. | [Calls and spawns, §1](about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls) |

## Channels and interactions

| Term | Definition | Canonical reference |
|---|---|---|
| **Channel** | A communication resource with identity and two endpoints. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Endpoint** | One participant-relative end of a shared channel. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Provider endpoint / client endpoint** | The role-relative endpoints of a process channel; the same channel is provider-side for one process incarnation and client-side for the other. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Provider channel / client channel** | A channel viewed from the process incarnation providing or using the service, respectively. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Channel placeholder** | A syntactic name in an expression or interface that stands for a channel; it is not the channel resource itself. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Channel identity** | The identifier of a channel resource, distinct from a placeholder or incarnation identifier. | [Incarnations and channels, §2–3](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Channel binding** | A local association between a placeholder and a channel identity in an incarnation's execution state. | [Processes and session types, §2, §7](about-processes-and-session-types/README.md#2-core-concepts) |
| **Logical transaction channel** | The stable pool-to-pool communication relationship for a fixed provider/client pair, represented by distinct public and private physical channels. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Public transaction channel** | The physical representation used while private access is inactive. | [Pools and transaction types, §5](about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel) |
| **Private channel** | A physical representation activated by matched `Up`; matched `Down` commits it, while pre-commit cancellation discards its uncommitted state. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **Communication exchange** | The exchange-level context in which endpoint operations and communication turns are matched; it is distinct from an individual channel identity. | [Pools and transaction types, §8](about-pools-and-transaction-types/README.md#8-implementation-mapping-and-evidence); [Processes and session types, §11](about-processes-and-session-types/README.md#11-execution-and-communication) |
| **Pending interaction** | A publication or subscription awaiting its corresponding peer action; it is not yet a completed interaction. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Matching** | The point at which corresponding endpoint actions meet and establish the shared interaction effect specified by the domain protocol. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Continuation expression** | The expression a participant may execute after its operation matches, subject to that operation's contract. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls); [Pools and transaction types, §6.2](about-pools-and-transaction-types/README.md#62-matched-transitions-continuations-and-channel-identity) |

## Protocols and agreements

| Term | Definition | Canonical reference |
|---|---|---|
| **Transaction** | A pool-to-pool interaction concerned with establishing or modifying an agreement. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Transaction type** | The protocol governing permitted pool interactions and transitions of agreement state. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Session type** | The protocol governing communication on a process channel, described from the provider endpoint's point of view. | [Processes and session types, §2, §6](about-processes-and-session-types/README.md#6-session-types-the-protocol-for-a-channel) |
| **Residual protocol state** | The part of a transaction or session protocol remaining after prior interaction steps. | [Processes and session types, §2–3](about-processes-and-session-types/README.md#2-core-concepts) |
| **Agreement** | The committed allocation state associated with a logical transaction channel and accepted by its participating pools. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **Process allocation function (`Q`)** | The per-logical-transaction-channel function assigning non-negative allocation weights to process names in the provider pool's competence set. | [Calls and spawns, §2](about-calls-and-spawns/README.md#2-process-spawning-and-the-pool-protocol); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |
| **Allocation state** | The value of `Q` at a particular point in a private-channel access; it may be committed or uncommitted. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **`Coop`** | A model-level allocation operation that increases the allocation weight for a named process. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |
| **`Hire` / `Apply`** | The two participant-side forms corresponding to the single model operation `Coop`; they are not separate model operations. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |
| **`Isol`** | A model-level allocation operation that decreases the allocation weight for a named process, subject to non-negativity. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |
| **`Fire` / `Quit`** | The two participant-side forms corresponding to the single model operation `Isol`; they are not separate model operations. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |
| **`ExternalCall`** | A named-process call that obtains service through pool selection and delivers a fresh provider channel to the caller. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) |
| **`InternalCall`** | A named-process call that creates a fresh incarnation in the invoking incarnation's pool and transfers its complete channel environment to it. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) |
| **Call** | The umbrella term for `ExternalCall` and `InternalCall`. | [Processes and session types, §5](about-processes-and-session-types/README.md); [Calls and spawns, §1](about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls) |
| **`spawn`** | A transaction-type constructor permitting process spawning only when its allocation weight on the relevant channel is positive; it does not itself change `Q`. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules) |

## Related implementation terminology

The identifiers `CompRef`, `CommRef`, `ChnlID`, `ChnlPH`, `ExpVK`, `LiabSide`, `AssetSide`, `LinearRec`, `StructRec`, `PubRec`, and `SubRec` are implementation names, not additional OrgLang model terms. Their observed correspondence is recorded in the specifications that own the relevant execution paths:

- [Pools and transaction types — implementation mapping and evidence](about-pools-and-transaction-types/README.md#8-implementation-mapping-and-evidence)
- [Processes and session types — implementation mapping and execution evidence](about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions)
- [Incarnations and channels](about-incarnations-and-channels/README.md) defines the abstract concepts independently of those implementation mappings.
