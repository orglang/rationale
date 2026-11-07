# Computations and communications

> **Status: preliminary semantic research.** This document describes abstract execution and communication mechanisms that are independent of any particular domain model.

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## Part I. Conceptual model

### 1. Computation and execution

A **Computation** is an aggregate in the computational context, rooted at an **Execution**. The **Execution** aggregate root represents a concrete execution and has its own unique identifier and **execution state**. Applications and reductions unfold within an execution.

The aggregate root is the entity through which the aggregate is identified and accessed. This description does not prescribe additional cardinality or lifecycle rules.

A computation is not an identifier, a term, or a channel. An identifier may refer to a runtime resource; a term describes an action or expression; a channel provides a communication relation between two participant-relative endpoints.

### 2. Identifiers and placeholders

An **identifier** names or refers to a runtime resource. In the abstract notation below, identifiers are written with early Latin letters such as *a*, *b*, and *c*.

A **placeholder** is a syntactic name whose runtime referent is supplied by **placeholder replacement**. Placeholders are written with late Latin letters such as *x*, *y*, and *z*. A placeholder is not itself the resource to which it is bound: after replacement, the identifier occupies that syntactic position. A Placeholder is unique within its containing declaration, definition, or expression.

This distinction is important for channel references. An identifier denotes the channel or other resource referred to at runtime; a Placeholder designates a variable within its static context.

### 3. Channels and endpoints

An **Exchange** is the stable communication aggregate root, with its own unique identifier. It has two persistent logical **endpoints**: a **provider endpoint** and a **client endpoint**. These endpoints are the two participant-relative sides of the Exchange; their identities persist throughout the Exchange, independently of the channels used for individual interactions.

A **channel** is a communication resource used by the two endpoints of an Exchange for an individual interaction. A corresponding pair consisting of a **Publication** and a **Subscription** is one interaction and is associated with a newly created channel with its own unique identifier. Thus, an Exchange may use a succession of distinct channels while retaining the same provider and client endpoints. A channel identifier, an Exchange identifier, a local placeholder, and an execution identifier are distinct kinds of reference. Their representations must not be conflated.

Each endpoint is accessed through a **Binding**. A Binding relates a particular revision of an Execution to a particular revision of an Exchange. These revisions are designated independently by an **Execution Reference** and an **Exchange Reference**, each including the identifier and revision of the referenced aggregate root. The Binding identifies a variable by the pair of Execution and **Placeholder**, and a channel by its **Channel Identifier**. The Execution context identifies the Definition whose expression provides the static context in which the Placeholder is unique. The Channel Identifier independently identifies the channel; no additional channel context is required for its identification. The association is further scoped by the Exchange and the relevant **Endpoint**. The provider endpoint carries the **provider channel-servicing responsibility**; the client endpoint carries the **client usage right**. These are distinct, complementary relations, not exclusive ownership of the channel as a whole.

A Binding is a domain relation between the participating aggregate contexts, rather than a part owned exclusively by either aggregate. It may therefore relate entities belonging to different aggregates. This does not by itself require Binding to be a separate aggregate; its storage and coordination model remain open. Execution and Exchange are peers in this domain relation.

Binding is a domain fact in its own right, not merely a technical representation of a successful Matching. It relates particular revisions of the participating roots and remains meaningful as a historical fact after either aggregate has completed. The history of these relations should arise from the sequence of positive and negative Binding facts; this does not prescribe a separate history mechanism or where such facts are stored.

A positive Binding arises when a Publication and a Subscription in the Exchange match. The Publication and Subscription are initiated from Execution contexts. The model does not currently prohibit both actions from being initiated by the same Execution.

Consistency of a Binding across the participating aggregate contexts requires coordination. If Execution and Exchange are separate aggregates, coordination may be provided externally or by the aggregate that initiates the operation; which aggregate can act as initiator depends on the chosen aggregate boundaries. The current working assumption is synchronous coordination: Matching completes only after the participating aggregate states are consistent, and failure to update either side must not leave the change to the other side committed. This coordination requirement does not decide whether Execution and Exchange are separate aggregates or belong to one aggregate.

An Exchange is designated by its own **unique identifier**. Each channel is also designated by a separate **unique identifier**. A channel's type expression is identified by a **content key**, a hash of the expression's content. This separates the identity of the Exchange and channel resources from the content-based designation of the type expression.

#### Channel rights, responsibilities, and bindings

**Client usage right** is the right of the participant associated through the client endpoint to use the channel according to its type. **Provider channel-servicing responsibility** is the obligation of the participant associated through the provider endpoint to service the channel according to its type. Neither relation implies or replaces the other.

In the dynamic model, a **Binding** represents this association without embedding the complete static **Variable** or **Channel** entities. A **positive binding** records establishment of the association; a **negative binding** records its release.

By **linearity**, one Endpoint may have at most one active binding at a time. A new positive Binding for an Endpoint must not become committed before the negative Binding releasing its previous association has been committed. The release and establishment may be committed together in one atomic transaction, in which case the intermediate unbound state is not observable. Alternatively, the Endpoint may remain temporarily unbound until a later positive Binding is established. The permitted duration of that state and the timeout or rollback behavior depend on the particular operation; there is no general timeout or rollback rule at this level.

The Endpoint remains the same historical entity throughout; releasing a binding does not remove the Endpoint. A period with no active binding is permitted, including while a channel is being sent as a value over another channel and before the recipient establishes its binding.

A **transfer of client usage right** or **provider channel-servicing responsibility** may be defined as a direct handoff between executions. Where a call contract specifies such a handoff as atomic, it is observed as one indivisible change, without an intermediate state in which the right or responsibility is unassigned or assigned to multiple executions. This atomic handoff rule does not prescribe the behavior of sending a channel as a value over another channel: in that case, the source binding may be released before the recipient establishes a new binding. The channel's identity and the Exchange's endpoint identities remain unchanged.

An **ExternalCall** may transfer client usage rights for supplied channels while leaving the corresponding provider channel-servicing responsibilities with their existing providers. An **InternalCall** transfers the complete channel environment of the old execution to the new execution: client usage rights for client-side bindings and provider channel-servicing responsibilities for provider-side bindings. In both cases, peer participants' complementary relations remain in place.

## Part II. Abstract communication model

### 4. Publication, subscription, and matching

The abstract term forms are:

| Term | Meaning |
| :--- | :--- |
| *c* ← *a* | Bind or connect the local channel reference *c* to the channel identified by *a*. |
| *c*.*V* | Publish value *V* on channel *c*. |
| `case` *c* *K* | Subscribe on channel *c* with continuation *K*. |

**Publication** and **subscription** are complementary endpoint actions. A publication that has no matching subscription remains pending; a subscription that has no matching publication also remains pending. The communication interaction takes effect when the corresponding actions match. Matching makes the received value available to the subscription's continuation; it does not imply that both computations execute simultaneously.

The concrete values, permitted interactions, and continuation obligations are defined by the domain-specific model using the channel. **Communication** is an aggregate in the communication context, rooted at an **Exchange**. The **Exchange** aggregate root represents an ordered sequence of communication **Acts**, each of which is a publication or a subscription. A corresponding Publication/Subscription pair constitutes one interaction and is associated with its own Channel; both Acts in the pair refer to that Channel. The Exchange's provider and client endpoints persist across these interactions.

### 5. Values and continuations

*V* is a metavariable for a value supplied by a domain-specific model. *K* is a metavariable for a **term continuation**: a continuation that selects the next term after a value is matched and applied. This is distinct from process-level continuation eligibility, which determines when a process may execute again, and from a **type continuation**, which describes the interactions permitted after the current interaction. In the abstract notation, a term continuation may be represented as a collection of value-pattern/continuation pairs:

`K ::= (V ⇒ P) | (V₁ ⇒ P₁, …, Vₙ ⇒ Pₙ)`

Here *P* and *Pᵢ* are terms. This notation does not define a concrete value constructor or branch-selection policy; those are owned by the relevant domain specification.

### 6. Placeholder replacement and continuation application

Placeholder replacement replaces a placeholder in a term with an identifier. We write *P*[*a*/*x*] for the result of replacing the free occurrences of placeholder *x* in *P* with identifier *a*.

When a published value matches a continuation pattern, applying the value to the continuation selects the corresponding branch and performs the required placeholder replacements. We write this abstract operation as *V* ▷ *K*. It is defined only when the value matches a pattern in *K*; otherwise the application is undefined.

The exact matching relation between values and patterns, and the placeholder replacements performed by a successful application, depend on the value grammar defined by the relevant domain model.

### 7. Types and constraints

Type expressions may be composed using connectives of different arities: unary, binary, or n-ary. A type expression may also carry a **constraint** or **refinement** that restricts the states or values for which an interaction is permitted.

This section establishes only the general vocabulary of type expressions, connectives, constraints, and refinements. Concrete constructors, duality rules, and typing judgments are defined by the domain-specific models.

## Part III. Relation to prior work

### 8. Continuation-based communication

The abstract distinction between a published value and a continuation waiting to consume it follows the general channel-and-continuation style used in the supplied channel-calculus literature. In that style, communication supplies a value, and applying that value to a continuation determines the next term through pattern selection and substitution.

This correspondence is a source of conceptual structure, not a claim that the publication defines OrgLang's concrete value constructors or language semantics.

## Part IV. Open questions

The abstract model leaves the following representation and semantics questions open:

- Which identifier classes are distinct at the language level, and what uniqueness guarantees apply to each?
- What record structure and storage arrangement should represent positive and negative Binding facts and their history?
- What are the general channel lifecycle and resource-reclamation rules?
- What ordering and observability guarantees apply to pending publication/subscription actions and their match?
- Which general typing rules govern channel references, values, and continuations independently of a particular domain model?

These questions should be resolved at the abstract mechanism layer only when their answers are independent of a particular domain model.
