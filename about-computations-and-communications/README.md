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

A **placeholder** is a syntactic name whose runtime referent is supplied by **placeholder replacement**. Placeholders are written with late Latin letters such as *x*, *y*, and *z*. A placeholder is not itself the resource to which it is bound: after replacement, the identifier occupies that syntactic position.

This distinction is important for channel references. A placeholder is local to an expression or continuation; an identifier denotes the channel or other resource referred to at runtime.

### 3. Channels and endpoints

An **Exchange** is the stable communication aggregate root, with its own unique identifier. It has two persistent logical **endpoints**: a **provider endpoint** and a **client endpoint**. These endpoints are the two participant-relative sides of the Exchange; their identities persist throughout the Exchange, independently of the channels used for individual interactions.

A **channel** is a communication resource used by the two endpoints of an Exchange for an individual interaction. A corresponding pair consisting of a **Publication** and a **Subscription** is one interaction and is associated with a newly created channel with its own unique identifier. Thus, an Exchange may use a succession of distinct channels while retaining the same provider and client endpoints. A channel identifier, an Exchange identifier, a local placeholder, and an execution identifier are distinct kinds of reference. Their representations must not be conflated.

Each endpoint is accessed through a **Binding** that identifies a variable by its **Placeholder** and a channel by its **Identifier**. The association is scoped by an **Execution**, an **Exchange**, and the relevant **Endpoint**. The provider endpoint carries the **provider channel-servicing responsibility**; the client endpoint carries the **client usage right**. These are distinct, complementary relations, not exclusive ownership of the channel as a whole.

An Exchange is designated by its own **unique identifier**. Each channel is also designated by a separate **unique identifier**. A channel's type expression is identified by a **content key**, a hash of the expression's content. This separates the identity of the Exchange and channel resources from the content-based designation of the type expression.

#### Channel rights, responsibilities, and bindings

**Client usage right** is the right of the participant associated through the client endpoint to use the channel according to its type. **Provider channel-servicing responsibility** is the obligation of the participant associated through the provider endpoint to service the channel according to its type. Neither relation implies or replaces the other.

In the dynamic model, a **Binding** represents this association without embedding the complete static **Variable** or **Channel** entities. A **positive binding** records establishment of the association; a **negative binding** records its release.

By **linearity**, one Endpoint may have at most one active binding at a time. Its binding may end and a later binding may associate the same Endpoint with another Execution and/or another Channel. The Endpoint remains the same historical entity throughout; releasing a binding does not remove the Endpoint. A period with no active binding is permitted, including while a channel is being sent as a value over another channel and before the recipient establishes its binding.

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
- What are the exact rules for interpreting positive and negative binding records, including their history and scope?
- What are the general channel lifecycle and resource-reclamation rules?
- What ordering and observability guarantees apply to pending publication/subscription actions and their match?
- Which general typing rules govern channel references, values, and continuations independently of a particular domain model?

These questions should be resolved at the abstract mechanism layer only when their answers are independent of a particular domain model.
