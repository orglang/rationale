# OrgLang glossary

> **Status: informative terminology reference.** This glossary records the shared vocabulary used across the OrgLang research documents. It summarizes concepts; it does not introduce or replace language rules. The linked canonical documents remain authoritative for detailed definitions, constraints, and lifecycle rules. Where a concept is still a working model, its status in that document remains authoritative.

Implementation identifiers are deliberately excluded. Their correspondence to model concepts belongs in the relevant specification's **Implementation concretization** material and is tied to a specific inspected source snapshot.

## Participants and executions

| Term | Definition | Canonical reference |
|---|---|---|
| **Participant** | A pool or process incarnation taking part in a channel interaction. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-participants-and-channels) |
| **Pool** | A participant that communicates with other pools and may service a process incarnation under an agreement. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Pool term** | An executable expression describing a pool's communication or state transition. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Process** | The general concept of a process; context determines whether it refers to a named process or a running incarnation. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Named process** | A process identified by a name, with a declaration and definition. | [Processes and session types, §2, §4](about-processes-and-session-types/README.md#2-core-concepts) |
| **Process declaration** | The interface of a named process, including its channel parameters. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Process definition** | The body or expression specifying the behavior of a named process. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Process incarnation** | One concrete running instance of a process. The current model assigns each incarnation a never-reused identity. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Servicing pool** | The pool associated with a process incarnation and responsible for servicing its provider channel. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-participants-and-channels) |
| **Execution reference** | A reference identifying a particular pool or process execution; it is not the execution's full state or a channel identity. | [Incarnations and channels, §6.3](about-incarnations-and-channels/README.md#63-implementation-concretization) |

## Channels and interactions

| Term | Definition | Canonical reference |
|---|---|---|
| **Channel** | A communication resource with identity, endpoints, and protocol state. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-participants-and-channels) |
| **Provider endpoint / client endpoint** | The role-relative endpoints of a shared channel. The same channel is the provider channel for one participant and a client channel for the other. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-participants-and-channels) |
| **Provider channel / client channel** | A channel viewed from the participant providing or using the service, respectively. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-participants-and-channels) |
| **Channel placeholder** | A syntactic name in an expression or interface that stands for a channel; it is not the channel resource itself. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Channel identity** | The identifier of a channel resource, distinct from a placeholder, communication reference, or execution reference. | [Incarnations and channels, §6.3](about-incarnations-and-channels/README.md#63-implementation-concretization) |
| **Channel binding** | A participant-local association between a placeholder and a channel, together with the relevant execution, communication, and protocol context. | [Incarnations and channels, §6.3](about-incarnations-and-channels/README.md#63-implementation-concretization) |
| **Logical transaction channel** | The stable pool-to-pool communication relationship for a fixed provider/client pair, represented by distinct public and private physical channels. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-concepts-and-terminology) |
| **Public transaction channel** | The physical representation used while private access is inactive. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **Private channel** | A physical representation activated by matched `Up`; matched `Down` commits it, while pre-commit cancellation discards its uncommitted state. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **Communication exchange** | The exchange-level context in which participant operations and turns are matched; it is distinct from an individual channel identity. | [Incarnations and channels, §6.3](about-incarnations-and-channels/README.md#63-implementation-concretization) |
| **Pending interaction** | An operation registered while waiting for its matching peer operation; it is not yet a completed interaction. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-common-matching-principle) |
| **Matching** | The point at which corresponding participant-side operations meet and establish the shared interaction effect specified by the protocol. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-common-matching-principle) |
| **Continuation expression** | The expression a participant may execute after its operation matches, subject to that operation's contract. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) |

## Protocols and agreements

| Term | Definition | Canonical reference |
|---|---|---|
| **Transaction** | A pool-to-pool interaction concerned with establishing or modifying an agreement. | [What is a transaction?](about-transaction/README.md) |
| **Transaction type** | The protocol governing permitted pool interactions and transitions of agreement state. | [Pools and transaction types, §2.1, §4](about-pools-and-transaction-types/README.md) |
| **Session type** | The protocol governing communication on a process channel, described from the provider endpoint's point of view. | [Processes and session types, §2, §6](about-processes-and-session-types/README.md) |
| **Residual protocol state** | The part of a transaction or session protocol remaining after prior interaction steps. | [Processes and session types, §2–3](about-processes-and-session-types/README.md#2-core-concepts) |
| **Agreement** | The committed allocation state associated with a logical transaction channel and accepted by its participating pools. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **Process allocation function (`Q`)** | The per-logical-transaction-channel function assigning non-negative allocation weights to process names in the provider pool's competence set. | [What is a transaction? — Types, constraints, refinements](about-transaction/README.md#типы-ограничения-уточнения) |
| **Allocation state** | The value of `Q` at a particular point in a private-channel access; it may be committed or uncommitted. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-protocol-and-established-agreement) |
| **`Coop`** | One model-level allocation operation that increases the allocation weight for a named process. | [What is a transaction?](about-transaction/README.md) |
| **`Hire` / `Apply`** | The two participant-side forms corresponding to the single model operation `Coop`; they are not separate model operations. | [Pools and transaction types, §4.1](about-pools-and-transaction-types/README.md) |
| **`Isol`** | One model-level allocation operation that decreases the allocation weight for a named process, subject to non-negativity. | [What is a transaction?](about-transaction/README.md) |
| **`Fire` / `Quit`** | The two participant-side forms corresponding to the single model operation `Isol`; they are not separate model operations. | [Pools and transaction types, §4.1](about-pools-and-transaction-types/README.md) |
| **`ExternalCall`** | A named-process call that obtains service through pool selection and delivers a fresh provider channel to the caller. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) |
| **`InternalCall`** | A named-process call that creates a fresh incarnation in the invoking incarnation's pool and transfers its complete channel environment to it. | [Processes and session types, §7](about-processes-and-session-types/README.md#7-intended-semantics-of-named-process-calls) |
| **Call** | The umbrella term for `ExternalCall` and `InternalCall`. | [Processes and session types, §5, §7](about-processes-and-session-types/README.md) |
| **`spawn`** | A transaction-type constructor permitting process spawning only when its allocation weight on the relevant channel is positive; it does not itself change `Q`. | [What is a transaction?](about-transaction/README.md) |

## Related implementation terminology

The identifiers `CompRef`, `CommRef`, `ChnlID`, `ChnlPH`, `ExpVK`, `LiabSide`, `AssetSide`, `LinearRec`, `StructRec`, `PubRec`, and `SubRec` are implementation names, not additional OrgLang model terms. Their observed correspondence is recorded in the relevant specifications:

- [Pools and transaction types — implementation concretization and evidence](about-pools-and-transaction-types/README.md#8-implementation-concretization-and-evidence)
- [Processes and session types — implementation mapping and execution evidence](about-processes-and-session-types/README.md#part-iii-implementation-evidence-and-open-questions)
- [Incarnations and channels — implementation concretization](about-incarnations-and-channels/README.md#63-implementation-concretization)
