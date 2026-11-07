# OrgLang glossary

> **Status: informative shared vocabulary.** This glossary collects concepts used across the OrgLang research documents. It summarizes common terminology but does not introduce or replace language rules. Domain-specific terms are defined in their owning specifications, which remain authoritative for their grammar, semantics, and constraints.

**Typography:** a shared term is bolded where it is first substantively introduced or defined in a document. Later occurrences are plain unless emphasis is needed for another reason. Boldface identifies vocabulary; it does not make a statement normative.


## Designation approaches

OrgLang uses three distinct approaches to designate entities or types:

| Approach | Definition | Typical use |
|---|---|---|
| **Qualified name** | Designation by a qualified symbol. | Static language entities, including types referred to by variables. |
| **Unique identifier** | Designation by a unique machine-oriented identifier. | Runtime entities and resources such as executions, exchanges, and channels. |
| **Content key** | Designation by a hash of expression content. | Expressions identified by their content. |

A **Reference** is an extended form of unique-identifier-based designation, not a separate basic designation approach; see its entry below.

## Model and execution

| Term | Definition | Canonical reference |
|---|---|---|
| **Execution** | The aggregate root of a **Computation** aggregate. It represents a concrete execution and has its own unique identifier and execution state. Applications and reductions unfold within an execution. Its short name in the implementation is `exec`. | [Executions and exchanges, §1](about-executions-and-exchanges/README.md#1-computation-and-execution) |
| **Execution state** | The abstract runtime state associated with a particular execution. | [Executions and exchanges, §1](about-executions-and-exchanges/README.md#1-computation-and-execution) |
| **Computation** | An aggregate in the computational context, rooted at an **Execution**. | [Executions and exchanges, §1](about-executions-and-exchanges/README.md#1-computation-and-execution) |
| **Process** | A domain-specific computational entity in the process model; context distinguishes its declaration and definition from a running computation. The process specification provides its full definition and is authoritative for its semantics. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Pool** | A domain-specific kind of participant in the pool model that makes capabilities available to other pools and may assume **pool process-servicing responsibility** for process computations under agreements. The pool specification provides its full definition and is authoritative for its semantics. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
| **Participant** | An entity that takes part in an interaction through a channel. | [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships); [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |

## Language structure

| Term | Definition | Canonical reference |
|---|---|---|
| **Symbol** | A syntactic designation (name) in the language. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Qualified symbol** | A symbol written with the qualification needed to distinguish it from other symbols, such as a module, namespace, or enclosing declaration path. The exact qualification components and resolution rules depend on the language's naming model. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Declaration** | A declaration consists of a qualified symbol, exactly one provider-side variable, and zero or more client-side variables. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Term declaration** | A declaration whose one provider-side variable and zero or more client-side variables are all term variables. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Type declaration** | A declaration whose one provider-side variable and zero or more client-side variables are all type variables. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Definition** | A definition consists of a qualified symbol and an expression. It refers to the unique declaration with the same qualified symbol; it does not introduce a name. Each declaration has exactly one definition, and each definition refers to exactly one declaration. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Term definition** | A definition that refers to a term declaration with the same qualified symbol and associates it with a term expression. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Type definition** | A definition that refers to a type declaration with the same qualified symbol and associates it with a type expression. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Variable** | A pair consisting of a placeholder (the variable's name) and a type, identified by a qualified symbol. | [Processes and session types, §4, §6](about-processes-and-session-types/README.md) |
| **Term variable** | A variable belonging to the term layer. | [Processes and session types, §4](about-processes-and-session-types/README.md#4-process-declarations-and-definitions) |
| **Type variable** | A variable belonging to the type layer. | [Processes and session types, §6](about-processes-and-session-types/README.md#6-session-types-for-a-channel) |
| **Placeholder** | A syntactic variable name that is unique within its containing declaration, definition, or expression. Its runtime referent is supplied through placeholder replacement; it is not itself the resource. | [Executions and exchanges, §2](about-executions-and-exchanges/README.md#2-identifiers-and-placeholders) |
| **Expression** | A formal expression of OrgLang belonging to either the term layer or the type layer. | [Executions and exchanges, §4, §7](about-executions-and-exchanges/README.md) |
| **Term expression** | A formal expression belonging to the term layer. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Type expression** | A formal expression belonging to the type layer. | [Executions and exchanges, §7](about-executions-and-exchanges/README.md#7-types-and-constraints) |

## Values and continuations

| Term | Definition | Canonical reference |
|---|---|---|
| **Value** | The structural side of the model; **Term** and **Type** are its two varieties. | [Executions and exchanges, §5](about-executions-and-exchanges/README.md#5-values-and-continuations) |
| **Term** | A variety of value belonging to the term layer. | [Executions and exchanges, §4–5](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Type** | A variety of value belonging to the type layer. | [Executions and exchanges, §7](about-executions-and-exchanges/README.md#7-types-and-constraints) |
| **Continuation** | The behavioral side of the model, at the same conceptual level as Value; it is not a variety of Value. | [Executions and exchanges, §5–6](about-executions-and-exchanges/README.md#5-values-and-continuations) |
| **Term continuation** | A variety of continuation belonging to the term layer. | [Executions and exchanges, §5–6](about-executions-and-exchanges/README.md#5-values-and-continuations) |
| **Type continuation** | A variety of continuation belonging to the type layer. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |

## Designation and substitution

| Term | Definition | Canonical reference |
|---|---|---|
| **Identifier** | A unique machine-oriented designation of a runtime entity or resource; it is distinct from a syntactic symbol or placeholder. | [Executions and exchanges, §2](about-executions-and-exchanges/README.md#2-identifiers-and-placeholders) |
| **Reference** | A designation of a runtime entity consisting of an identifier and optional additional components, such as a revision. A reference may omit the revision to designate the entity without pinning a particular state, or include one to designate a particular revision. | [Executions and exchanges, §2](about-executions-and-exchanges/README.md#2-identifiers-and-placeholders) |
| **Placeholder replacement** | The syntactic operation of replacing free occurrences of a placeholder in a term with an identifier. It is written *P*[*a*/*x*] and is distinct from the runtime substitution that establishes a variable–channel association. | [Executions and exchanges, §6](about-executions-and-exchanges/README.md#6-placeholder-replacement-and-continuation-application) |
| **Substitution** | An operation that establishes an association between a variable and a channel. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Binding** | A domain relation between a particular revision of an Execution and a particular revision of an Exchange, designated independently by an Execution Reference and an Exchange Reference. It identifies a variable by the Execution–Placeholder pair and a channel by its Channel Identifier, in the context of an Endpoint. It is a domain fact in its own right, not merely a technical representation of Matching, and may relate entities belonging to different aggregates without being owned exclusively by either. Execution and Exchange are peers in this relation. A positive Binding arises when a Publication and Subscription in the Exchange match; the actions are initiated from Execution contexts, which may currently be the same Execution. The history of Binding relations is intended to arise naturally from positive and negative Binding facts and remains meaningful after either participating aggregate completes. Whether Binding requires a separate aggregate, and how its facts are stored and coordinated, remain open. Linearity permits at most one active Binding per Endpoint. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#3-channels-and-endpoints) |

## Communication

| Term | Definition | Canonical reference |
|---|---|---|
| **Communication** | An aggregate in the communication context, rooted at an **Exchange**. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Exchange** | The stable aggregate root of a **Communication** aggregate, with its own unique identifier and persistent provider and client endpoints; it represents an ordered sequence of communication acts. | [Executions and exchanges, §3–4](about-executions-and-exchanges/README.md#3-channels-and-endpoints) |
| **Act** | An individual communication act within an exchange, representing either a publication or a subscription on a channel. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Channel** | A communication resource with its own unique identifier, used by the provider and client endpoints of an Exchange for one matched Publication/Subscription interaction; its type expression is identified by a content key. | [Executions and exchanges, §3–4](about-executions-and-exchanges/README.md#3-channels-and-endpoints) |
| **Client usage right** | The right of the client participant to use a channel according to its type. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Provider channel-servicing responsibility** | The provider process's obligation to service a channel according to its type. It is represented by the provider-side binding in an Execution. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Pool process-servicing responsibility** | The pool provider's responsibility to service a process computation under the terms of an agreement. It is distinct from the process's responsibility to service its provider channels. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement); [Calls and spawns, §1](about-calls-and-spawns/README.md#1-intended-semantics-of-named-process-calls) |
| **Positive binding** | A Binding fact that records establishment of an association following a Publication/Subscription match in an Exchange. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Negative binding** | A Binding fact that records release of an existing association. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Transfer of client usage right** | An atomic change of the execution holding the client-side binding and entitled to use the channel, represented by a negative binding in the source execution and a positive binding in the destination execution. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Transfer of provider channel-servicing responsibility** | An atomic change of the execution holding the provider-side binding and responsible for servicing the channel, represented by a negative binding in the source execution and a positive binding in the destination execution. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#channel-rights-and-responsibilities) |
| **Endpoint** | One of the two persistent participant-relative sides of an Exchange, Provider or Client, accessed through a Binding that relates an Execution, Exchange, Endpoint, and Channel. An Endpoint may be successively associated with different Executions and Channels; linearity permits at most one active Binding per Endpoint. A new positive Binding cannot be committed before the previous association's negative Binding is committed, though release and establishment may be committed in one atomic transaction. A temporarily unbound state is also permitted; its duration and timeout or rollback behavior depend on the particular operation. | [Executions and exchanges, §3](about-executions-and-exchanges/README.md#3-channels-and-endpoints) |
| **Provider endpoint** | The persistent provider side of an Exchange, through which a participant provides the service or initiates the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Client endpoint** | The persistent client side of an Exchange, through which a participant uses the service or takes part in the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Public channel** | A channel exposed as the public interaction point for a participant; in the pool model, the public transaction channel is the stable access point when no private access is active. | [Pools and transaction types, §5](about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel) |
| **Private channel** | A channel used for a private access associated with a logical transaction channel; in the pool model it has a distinct physical identity and carries the access-local allocation state. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md) |
| **Publication** | An action performed through an endpoint that makes a value available on a channel for a matching subscription. A publication may remain pending while it awaits the corresponding subscription. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Subscription** | An action performed through an endpoint that waits on a channel for a matching publication and supplies a continuation for the received value. A subscription may remain pending while it awaits the corresponding publication. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |
| **Matching** | The point at which corresponding endpoint actions meet and establish the shared interaction effect specified by the applicable type. | [Executions and exchanges, §4](about-executions-and-exchanges/README.md#4-publication-subscription-and-matching) |

## Protocol and type discipline

| Term | Definition | Canonical reference |
|---|---|---|
| **Protocol type** | A type that specifies, from the provider endpoint's perspective, the interactions permitted over a channel, the complementary actions expected from the client endpoint, and the continuations permitted after those interactions. Session types and transaction types are distinct specializations; the category does not imply shared syntax or identical state semantics. | [Processes and session types, §6](about-processes-and-session-types/README.md); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Session type** | A protocol type that describes the interactions permitted over a channel, expressed from the provider endpoint's point of view. | [Processes and session types](about-processes-and-session-types/README.md) |
| **Transaction type** | A protocol type that describes the transaction interactions permitted through a pool's transaction channel, including their continuations and applicable allocation-state changes. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Constraint** | A condition associated with a type expression that restricts the states or values for which an interaction is permitted. | [Executions and exchanges, §7](about-executions-and-exchanges/README.md#7-types-and-constraints) |
| **Refinement** | A restriction attached to a type expression that narrows the states or values it admits. | [Executions and exchanges, §7](about-executions-and-exchanges/README.md#7-types-and-constraints) |
| **Linearity** | A discipline governing channel use that prevents channel endpoints or bindings from being duplicated or silently discarded. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |

