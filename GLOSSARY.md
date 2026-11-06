# OrgLang glossary

> **Status: informative shared vocabulary.** This glossary collects concepts used across the OrgLang research documents. It summarizes common terminology but does not introduce or replace language rules. Domain-specific terms are defined in their owning specifications, which remain authoritative for their grammar, semantics, and constraints.

**Typography:** a shared term is bolded where it is first substantively introduced or defined in a document. Later occurrences are plain unless emphasis is needed for another reason. Boldface identifies vocabulary; it does not make a statement normative.


## Designation approaches

OrgLang uses three distinct approaches to designate entities or types:

| Approach | Definition | Typical use |
|---|---|---|
| **Qualified name** | Designation by a symbol together with the qualification needed to distinguish it within the language's naming model. | Static language entities, including types referred to by variables. |
| **Unique identifier** | Designation by a unique machine-oriented identifier that refers to one particular runtime entity or resource. | Runtime entities such as executions and channel addresses. |
| **Content key** | Designation by a content-derived key, typically a hash, that identifies content independently of where or when it occurs. | The type expression associated with a channel. |

## Execution and model entities

| Term | Definition | Canonical reference |
|---|---|---|
| **Execution** | A standalone runtime entity representing one concrete execution, with its own unique identifier and execution state. Its short name in the implementation is `exec`. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Execution state** | The abstract runtime state associated with a particular execution. | [Incarnations and channels, §1](about-incarnations-and-channels/README.md#1-incarnations-and-execution-state) |
| **Participant** | A pool or process incarnation taking part in a communication or transaction interaction. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships); [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Pool** | A participant that makes capabilities available to other pools and may service process incarnations under agreements. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Process** | A named computational entity; context distinguishes its declaration and definition from a running incarnation. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Declaration** | A declaration consists of a qualified symbol, exactly one provider-side variable, and zero or more client-side variables. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Definition** | A definition consists of a qualified symbol and an expression. It refers to the unique declaration with the same qualified symbol; it does not introduce a name. Each declaration has exactly one definition, and each definition refers to exactly one declaration. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Term declaration** | A declaration whose one provider-side variable and zero or more client-side variables are all term variables. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Term definition** | A definition that refers to a term declaration with the same qualified symbol and associates it with a term expression. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Symbol** | A syntactic designation (name) in the language. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Qualified symbol** | A symbol written with the qualification needed to distinguish it from other symbols, such as a module, namespace, or enclosing declaration path. The exact qualification components and resolution rules depend on the language's naming model. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Reference** | A designation of a runtime entity consisting of an identifier and optional additional components, such as a revision. A reference may omit the revision to designate the entity without pinning a particular state, or include one to designate a particular revision. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Term reference** | A reference to a term entity. Its precise representation and semantics remain to be specified. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Type reference** | A reference to a type entity. Its precise representation and semantics remain to be specified. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Identifier** | A unique machine-oriented designation of a runtime entity, analogous to an address; it is distinct from a syntactic symbol or placeholder. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Placeholder** | A syntactic variable name whose runtime referent is supplied through substitution; it is not itself the resource. | [Incarnations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Substitution** | An operation that establishes an association between a placeholder and an identifier. Whether and how this association relates to a runtime variable-to-channel binding remains open. | [Incarnations and channels, §6](about-incarnations-and-channels/README.md#6-substitution-and-continuation-application) |
| **Type declaration** | A declaration whose one provider-side variable and zero or more client-side variables are all type variables. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Type definition** | A definition that refers to a type declaration with the same qualified symbol and associates it with a type expression. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Qualified symbol** | A symbol written in qualified form. The mechanism and components of qualification are not specified here. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Variable** | A pair consisting of a placeholder (the variable's name) and a type, identified by a qualified symbol. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Term variable** | A variable belonging to the term layer. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Type variable** | A variable belonging to the type layer. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Binding** | An association between a variable and a channel within an execution. A variable has at most one binding in an execution; it may be unbound while awaiting a channel. When a channel arrives for an awaiting variable, it is bound to that variable. A new binding for the same variable replaces the previous binding. | [Incarnations and channels, §2–3](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Expression** | A syntactic expression belonging to either the term layer or the type layer. | [Incarnations and channels, §4, §7](about-incarnations-and-channels/README.md) |
| **Term expression** | An expression describing an action or computation. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Type expression** | An expression describing a type, including its permitted interactions and any applicable constraints or refinements. | [Incarnations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Term** | An abstract expression describing an action or computation. | [Incarnations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Value** | An item communicated through a channel and interpreted according to the applicable value grammar. | [Incarnations and channels, §5](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Continuation** | A continuation associated with a term or a type; its specific meaning depends on the layer of the model. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Term continuation** | A continuation that selects or supplies the next term after a value is matched and applied. | [Incarnations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Process continuation** | A process expression that becomes eligible for execution after the interaction that enables it. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Calls and spawns, §1](about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls) |
| **Type continuation** | The residual type expression that describes the interactions permitted after the current interaction, including any refinements that constrain the runtime states or values admitted at that point. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |

## Channels and communication

| Term | Definition | Canonical reference |
|---|---|---|
| **Channel** | A channel is defined by an address (a unique identifier) and a content key identifying its type expression. It belongs to one specific execution and is not shared between executions. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Content key** | A content identifier (hash) of a type expression, used to identify a channel's type by its content. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Endpoint** | One participant-relative end of a shared channel. | [Incarnations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Provider endpoint** | The endpoint from which a participant provides the service or initiates the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Client endpoint** | The complementary endpoint from which a participant uses the service or takes part in the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
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

