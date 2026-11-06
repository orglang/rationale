# Incarnations and channels

> **Status: preliminary semantic research.** This document describes abstract execution and communication mechanisms that are independent of any particular domain model.

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## Part I. Conceptual model

### 1. Incarnations and execution state

An **incarnation** is one concrete runtime instance of an executing entity. It has its own **execution state** and local namespace. Two incarnations may originate from the same declaration or description while remaining distinct runtime instances.

An incarnation is not an identifier, a term, or a channel. An identifier may refer to a runtime resource; a term describes an action or expression; a channel provides a communication relation between endpoints.

### 2. Identifiers and placeholders

An **identifier** names or refers to a runtime resource. In the abstract notation below, identifiers are written with early Latin letters such as *a*, *b*, and *c*.

A **placeholder** is a syntactic name whose runtime referent is supplied by **placeholder replacement**. Placeholders are written with late Latin letters such as *x*, *y*, and *z*. A placeholder is not itself the resource to which it is bound: after replacement, the identifier occupies that syntactic position.

This distinction is important for channel references. A placeholder is local to an expression or continuation; an identifier denotes the channel or other resource referred to at runtime.

### 3. Channels and endpoints

A **channel** is a communication resource connecting two endpoints. Each endpoint is interpreted relative to its owning incarnation. The two endpoints refer to the same communication relation, while each incarnation maintains its own local references and execution state.

A channel identifier, a local placeholder, and an incarnation identifier are distinct kinds of reference. Their representations must not be conflated.

## Part II. Abstract communication model

### 4. Publication, subscription, and matching

The abstract term forms are:

| Term | Meaning |
| :--- | :--- |
| *c* ← *a* | Bind or connect the local channel reference *c* to the channel identified by *a*. |
| *c*.*V* | Publish value *V* on channel *c*. |
| `case` *c* *K* | Subscribe on channel *c* with continuation *K*. |

**Publication** and **subscription** are complementary endpoint actions. A publication that has no matching subscription remains pending; a subscription that has no matching publication also remains pending. The communication interaction takes effect when the corresponding actions match. Matching makes the received value available to the subscription's continuation; it does not imply that both incarnations execute simultaneously.

The concrete values, permitted interactions, and continuation obligations are defined by the domain-specific model using the channel. An **exchange** is an ordered sequence of communication **acts**, each of which is a publication or a subscription on a channel.

### 5. Values and continuations

*V* is a metavariable for a value supplied by a domain-specific model. *K* is a metavariable for a **term continuation**: a continuation that selects the next term after a value is matched and applied. This is distinct from a **process continuation**, which becomes eligible for execution, and a **type continuation**, which describes the interactions permitted after the current interaction. In the abstract notation, a term continuation may be represented as a collection of value-pattern/continuation pairs:

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

- What is the complete identity and lifetime contract for incarnations?
- Which identifier classes are distinct at the language level, and what uniqueness guarantees apply to each?
- What is the exact binding and substitution discipline, including scope, capture avoidance, and linearity?
- What are the general channel lifecycle and resource-reclamation rules?
- What ordering and observability guarantees apply to pending publication/subscription actions and their match?
- Which general typing rules govern channel references, values, and continuations independently of a particular domain model?

These questions should be resolved at the abstract mechanism layer only when their answers are independent of a particular domain model.
