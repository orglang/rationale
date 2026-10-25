<!-- Canonical semantics: pool and transaction-type model; process/pool selection remains in ../about-spawn/README.md -->

# Pools and transaction types

> **Status: preliminary semantic research.** This document is a technical companion to [What is a transaction?](../about-transaction/README.md). It collects the language-level model of pools and transaction types, distinguishes intended semantics from publication rules and implementation observations, and records unresolved questions. Its conclusions remain research findings pending a normative specification.

**Scope and document boundaries**

- This document owns the technical model of pools and transaction types, including the pool's public transaction channel and its protocol.
- [Process creation and pool selection](../about-spawn/README.md) owns pool eligibility, search order, process-incarnation creation, pool binding, and the start of servicing.
- [What is a transaction?](../about-transaction/README.md) provides the accessible introduction.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process expressions and the intended semantics of `ExternalCall` and `InternalCall`.

## 1. Scope, evidence, and status

This research draft keeps language-level intended semantics, claims made by the supplied publication, and implementation observations separate. A normative language specification remains future work.

Use the claim-status vocabulary from [Processes and session types, Section 1](../about-processes-and-session-types/README.md#1-scope-and-evidence): **Confirmed**, **Inferred**, and **Open**. Record the source and what it establishes for substantial or disputed claims. Implementation coverage is a separate dimension and should be recorded only when the relevant code path or test has been inspected.

## 2. Core concepts and terminology

_TODO: Define pool, pool term, transaction, transaction identifier, transaction type, public transaction channel, and the distinction between a pool's transaction protocol and a process provider channel._

## 3. Pool model

_TODO: Describe the intended pool model, state, and boundaries. Keep process-incarnation selection and servicing in [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing)._

## 4. Transaction types

_TODO: Specify the transaction-type constructors, their syntax, constraints, and intended interpretation. Distinguish established rules from candidate interpretations and implementation mappings._

**Open:** the precise encoding of pool eligibility in a pool's transaction type remains to be established. **Inferred:** the transaction type is a candidate signal for whether that pool can service a process with a given name. The search procedure is documented in [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing). Any additional runtime validation is also **Open**.

**Tentative project direction:** transaction types are expected to be based on dependent-type mechanisms. How transaction types relate to pool agreements remains open. Under this direction, the agreement-search timeout might be expressed through a transaction-type parameter, but this remains a design hypothesis, not a defined type constructor or formal rule. The timeout's operational boundary is specified in [Process creation and pool selection, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). Its source, syntax, parameter instantiation, checking rules, and whether its value is statically fixed or dynamically determined remain open.

## 5. The pool's public transaction channel

**Inferred:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public transaction channel. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Inferred:** access through the pool's public transaction channel gives the client a private channel for the duration of the critical section. Exclusivity applies to this private channel and its interaction; separate client interactions fall outside that scope. Reaching `Down` marks the end of this protocol-bounded critical section; the client interaction along that channel continuation ends there.

Each interaction generates a new channel identifier for its continuation, reflected in the channel's type. Resource lifecycle after `Down`—closure, return to the pool, or another disposition—remains unspecified pending a precise account of the `Up` / continuation / `Down` semantics.

This pool-level protocol is conceptually distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Process creation and pool selection](../about-spawn/README.md).

## 6. Intended semantics and formal rules

_TODO: State candidate or agreed language-level rules, including preconditions, transitions, continuation behavior, and resource/transaction lifecycle. Identify the evidence for each rule._

## 7. Publication correspondence

_TODO: Compare the relevant publication's rules with the OrgLang model. A publication rule establishes what that publication says; correspondence to OrgLang remains a separate claim._

## 8. Implementation evidence

_TODO: Map transaction-type and pool concepts to implementation structures and execution paths. Record file/symbol evidence, coverage status, and mismatches. Treat names as clues; establish language semantics from appropriate evidence._

## 9. Open questions and next tests

- How are agreement parameters, including timeout values, represented and checked if transaction types are based on dependent-type mechanisms?
- What exactly do `Up` and `Down` guarantee about the transaction protocol and its continuation?
- What happens to the private channel and any associated resources after `Down`?
- Are public channels a pool-only concept, or can individual processes expose them as well?
- What are the precise syntax, typing constraints, and transition rules for each transaction-type constructor?
- Which implementation paths and tests establish conformance to the intended model?

_TODO: Add source-specific questions and tests as the model is verified._
