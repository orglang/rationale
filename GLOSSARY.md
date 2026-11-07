# OrgLang glossary

> **Status: informative shared vocabulary.** This glossary collects concepts used across the OrgLang research documents. It summarizes common terminology but does not introduce or replace language rules. Domain-specific terms are defined in their owning specifications, which remain authoritative for their grammar, semantics, and constraints.

**Typography:** a shared term is bolded where it is first substantively introduced or defined in a document. Later occurrences are plain unless emphasis is needed for another reason. Boldface identifies vocabulary; it does not make a statement normative.


## Designation approaches

OrgLang uses three distinct approaches to designate entities or types:

| Approach | Definition | Typical use |
|---|---|---|
| **Qualified name** | Designation by a qualified symbol. | Static language entities, including types referred to by variables. |
| **Unique identifier** | Designation by a unique machine-oriented identifier. | Runtime entities such as executions and channels. |
| **Content key** | Designation by a hash of expression content. | Expressions identified by their content. |

A **Reference** is an extended form of unique-identifier-based designation, not a separate basic designation approach; see its entry below.

## Model and execution

| Term | Definition | Canonical reference |
|---|---|---|
| **Execution** | The aggregate root of a **Computation** aggregate. It represents a concrete execution and has its own unique identifier and execution state. Applications and reductions unfold within an execution. Its short name in the implementation is `exec`. | [Computations and channels, §1](about-incarnations-and-channels/README.md#1-computation-and-execution) |
| **Execution state** | The abstract runtime state associated with a particular execution. | [Computations and channels, §1](about-incarnations-and-channels/README.md#1-computation-and-execution) |
| **Computation** | An aggregate in the computational context, rooted at an **Execution**. | [Computations and channels, §1](about-incarnations-and-channels/README.md#1-computation-and-execution) |
| **Process** | A domain-specific computational entity in the process model; context distinguishes its declaration and definition from a running computation. The process specification provides its full definition and is authoritative for its semantics. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Pool** | A domain-specific kind of participant in the pool model that makes capabilities available to other pools and may service process computations under agreements. The pool specification provides its full definition and is authoritative for its semantics. | [Pools and transaction types](about-pools-and-transaction-types/README.md) |
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
| **Placeholder** | A syntactic variable name whose runtime referent is supplied through placeholder replacement; it is not itself the resource. | [Computations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Expression** | A formal expression of OrgLang belonging to either the term layer or the type layer. | [Computations and channels, §4, §7](about-incarnations-and-channels/README.md) |
| **Term expression** | A formal expression belonging to the term layer. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Type expression** | A formal expression belonging to the type layer. | [Computations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |

## Values and continuations

| Term | Definition | Canonical reference |
|---|---|---|
| **Value** | The structural side of the model; **Term** and **Type** are its two varieties. | [Computations and channels, §5](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Term** | A variety of value belonging to the term layer. | [Computations and channels, §4–5](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Type** | A variety of value belonging to the type layer. | [Computations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Continuation** | The behavioral side of the model, at the same conceptual level as Value; it is not a variety of Value. | [Computations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Term continuation** | A variety of continuation belonging to the term layer. | [Computations and channels, §5–6](about-incarnations-and-channels/README.md#5-values-and-continuations) |
| **Type continuation** | A variety of continuation belonging to the type layer. | [Processes and session types, §3](about-processes-and-session-types/README.md#3-a-small-example-following-a-channel); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |

## Designation and substitution

| Term | Definition | Canonical reference |
|---|---|---|
| **Qualified name** | Designation by a qualified symbol. | Static language entities, including types referred to by variables. |
| **Unique identifier** | Designation by a unique machine-oriented identifier. | Runtime entities such as executions and channels. |
| **Identifier** | A unique machine-oriented designation of a runtime entity or resource; it is distinct from a syntactic symbol or placeholder. | [Computations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Reference** | A designation of a runtime entity consisting of an identifier and optional additional components, such as a revision. A reference may omit the revision to designate the entity without pinning a particular state, or include one to designate a particular revision. | [Computations and channels, §2](about-incarnations-and-channels/README.md#2-identifiers-and-placeholders) |
| **Content key** | A hash of an expression's content, used to identify that expression independently of where or when it occurs. | [Computations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Placeholder replacement** | The syntactic operation of replacing free occurrences of a placeholder in a term with an identifier. It is written *P*[*a*/*x*] and is distinct from the runtime substitution that establishes a variable–channel association. | [Computations and channels, §6](about-incarnations-and-channels/README.md#6-placeholder-replacement-and-continuation-application) |
| **Substitution** | An operation that establishes an association between a variable and a channel. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |
| **Binding** | An association between a variable and a channel recorded within an execution. Bindings have positive or negative polarity: a positive binding records the association, while a negative binding records its release. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |

## Communication

| Term | Definition | Canonical reference |
|---|---|---|
| **Communication** | An aggregate in the communication context, rooted at an **Exchange**. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Exchange** | The aggregate root of a **Communication** aggregate, representing an ordered sequence of communication acts. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Act** | An individual communication act within an exchange, representing either a publication or a subscription on a channel. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Channel** | A communication resource identified by a unique identifier and a content key identifying its type expression. Every channel is created with exactly one owning execution and always has exactly one owner. | [Computations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Channel ownership** | The exclusive relation between a channel and its single owning execution. | [Computations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Positive binding** | A binding record that establishes or records a channel association in an execution. | [Computations and channels, §3](about-incarnations-and-channels/README.md#channel-ownership-and-transfer) |
| **Negative binding** | A binding record that records release of a channel association by an execution. | [Computations and channels, §3](about-incarnations-and-channels/README.md#channel-ownership-and-transfer) |
| **Transfer of channel ownership** | An atomic change of a channel's owning execution, represented by a negative binding in the source execution and a positive binding in the destination execution. | [Computations and channels, §3](about-incarnations-and-channels/README.md#channel-ownership-and-transfer) |
| **Endpoint** | One participant-relative end of a shared channel. | [Computations and channels, §3](about-incarnations-and-channels/README.md#3-channels-and-endpoints) |
| **Provider endpoint** | The endpoint from which a participant provides the service or initiates the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Client endpoint** | The complementary endpoint from which a participant uses the service or takes part in the interaction described by a channel's type. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts); [Pools and transaction types, §2](about-pools-and-transaction-types/README.md#2-core-model-relationships) |
| **Public channel** | A channel exposed as the public interaction point for a participant; in the pool model, the public transaction channel is the stable access point when no private access is active. | [Pools and transaction types, §5](about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel) |
| **Private channel** | A channel used for a private access associated with a logical transaction channel; in the pool model it has a distinct physical identity and carries the access-local allocation state. | [Pools and transaction types, §2.1](about-pools-and-transaction-types/README.md) |
| **Publication** | An endpoint action that makes a value available on a channel for a matching subscription. A publication may remain pending while it awaits the corresponding subscription. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Subscription** | An endpoint action that waits on a channel for a matching publication and supplies a continuation for the received value. A subscription may remain pending while it awaits the corresponding publication. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |
| **Matching** | The point at which corresponding endpoint actions meet and establish the shared interaction effect specified by the applicable type. | [Computations and channels, §4](about-incarnations-and-channels/README.md#4-publication-subscription-and-matching) |

## Protocol and type discipline

| Term | Definition | Canonical reference |
|---|---|---|
| **Protocol type** | A type that specifies, from the provider endpoint's perspective, the interactions permitted over a channel, the complementary actions expected from the client endpoint, and the continuations permitted after those interactions. Session types and transaction types are distinct specializations; the category does not imply shared syntax or identical state semantics. | [Processes and session types, §6](about-processes-and-session-types/README.md); [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Session type** | A protocol type that describes the interactions permitted over a channel, expressed from the provider endpoint's point of view. | [Processes and session types](about-processes-and-session-types/README.md) |
| **Transaction type** | A protocol type that describes the transaction interactions permitted through a pool's transaction channel, including their continuations and applicable allocation-state changes. | [Pools and transaction types, §4](about-pools-and-transaction-types/README.md#4-transaction-types) |
| **Constraint** | A condition associated with a type expression that restricts the states or values for which an interaction is permitted. | [Computations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Refinement** | A restriction attached to a type expression that narrows the states or values it admits. | [Computations and channels, §7](about-incarnations-and-channels/README.md#7-types-and-constraints) |
| **Linearity** | A channel usage and ownership discipline that prevents channel endpoints or bindings from being duplicated or silently discarded. | [Processes and session types, §2](about-processes-and-session-types/README.md#2-core-concepts) |

