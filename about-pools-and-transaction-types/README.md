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

The following are **working definitions inferred from the current explanatory model**, not normative language definitions. The model is described in [What is a transaction?](../about-transaction/README.md); its correspondence to a complete OrgLang specification remains to be established.

| Term | Working meaning | Status and limitation |
|---|---|---|
| Pool | A participant that can communicate with other pools and may service a process incarnation under an agreement. | **Inferred** from the explanatory model and the current process–pool model. Pool lifecycle, internal state, and whether every incarnation must always be bound to one pool remain **Open**. |
| Pool term | An executable expression describing a pool's communication or state transition. | **Inferred** from the companion model's distinction between terms, values, and continuations. Its runtime representation in OrgLang is **Open**. |
| Transaction | A private communication relationship between pools, used to exchange protocol messages under an agreement. | **Inferred** from the explanatory model. A transaction is the communication relationship, not the agreement's terms; creation, ownership, cancellation, and completion rules are not fully specified. |
| Agreement | An established arrangement between a client pool and a servicing pool, whose terms are expressed by a transaction type. | **Inferred** from the current project model. The complete lifecycle and negotiation rules remain **Open**. |
| Transaction identifier | An identifier used to refer to a transaction or its channel in the pool model. | **Inferred**. Its concrete representation, allocation/uniqueness guarantees, and exact referent are **Open**. Do not assume it is identical to a process channel identity or to the agreement itself. |
| Transaction type | The protocol description that expresses the terms of an agreement and governs which transaction messages or transitions are permitted. | **Inferred** from the companion model's transaction-type grammar and the agreed project direction. Exact OrgLang syntax, checking rules, and runtime enforcement remain **Open**. |
| Pool's public transaction channel | The channel through which a client interacts with the pool-level transaction protocol. | **Inferred** from [issue #85](https://github.com/orglang/go-workspace/issues/85) and the current explanatory model. Whether individual processes can expose analogous public channels remains **Open**. |
| Process provider channel | The channel on which a process incarnation provides its named-process service. | Defined in [Processes and session types, Section 2](../about-processes-and-session-types/README.md#2-core-concepts). It is distinct from the pool's public transaction channel. |

A transaction identifier and a process channel identity must not be conflated merely because both are called identifiers or channels. The current model uses identifiers for different resources depending on interpretation; a precise mapping requires evidence from the language contract or a verified execution path.

For consistent usage in this document, distinguish the **transaction** (the pool-to-pool communication relationship), the **agreement** (the established arrangement between the pools), and the **transaction type** (the protocol terms expressing that agreement). The transaction type is not a separate compatibility mechanism: it is the agreement's protocol description. A **transaction identifier** refers to a transaction or its channel; it is not an agreement identifier unless a separate rule establishes that mapping.

## 3. Pool model

**Inferred working model:** a pool is represented by a pool term/state and exposes a public transaction channel. Other pools interact with it through transactions governed by a transaction type. This summary reflects the current explanatory model; it does not establish a complete operational semantics for pools in OrgLang.

The following boundaries are currently supported by the document set:

- Pool eligibility, search order, incarnation-to-pool association, and the start of servicing belong to [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing).
- The process's provider channel is distinct from the pool's public transaction channel.
- The protocol associated with the public transaction channel is described in Section 5 below.

The pool's state representation, lifecycle, ownership of resources, and behavior when it cannot service a request remain **Open**. These are semantic gaps, not assumed absences of behavior.

## 4. Transaction types

The companion [transaction introduction](../about-transaction/README.md) presents a candidate grammar that includes unit/termination, directional `Up` and `Down`, choice (`Plus`/`With`), pool-state constraints associated with `Coop`/`Isol`, and a process-spawn form. This is evidence for the notation used in that explanatory model, not proof that every constructor is part of the established OrgLang contract.

| Question | Current status | Why it matters | Evidence needed |
|---|---|---|---|
| Which constructors belong to the OrgLang transaction-type language, and what is their exact syntax? | **Open** | Determines what specifications and programs may express. | An adopted language grammar or an explicit project decision; compare with the companion model and implementation parser/type definitions. |
| What are the remaining exact transition rules for `One`, `Up`, and `Down`, including type-state progression, ownership, and observable boundaries? | **Partly decided; partly Open** | Matching is the transition point; the remaining state progression and observability details govern conformance. | Preserve Section 8.1 decisions; specify remaining obligations, then test permitted and prohibited transitions. |
| Which agreement-specific details, if any, supplement the agreed process-name match when determining pool suitability? | **Open** | The process-name match is the current agreed criterion; whether dependent type details further constrain suitability remains unsettled. | Define the role of dependent type details and add positive/negative examples; do not introduce a separate compatibility mechanism beyond the agreement itself. |
| Are constraints on pool state part of type checking, runtime validation, or both? | **Open** | Determines which constraints expressed by the transaction-type agreement are checked statically and which require runtime validation. | A typing/validation rule and implementation-path evidence, with negative examples. |
| How do dependent types express agreement-specific details, and how do those details participate in matching or instantiation? | **Open** | Determines how participant-specific or agreement-specific terms are expressed within the transaction-type agreement. | A project decision about dependent-type meaning and its role in matching/instantiation; the transaction type expresses the agreement's protocol terms, rather than acting as a separate compatibility mechanism. |

The detailed eligibility question and the evidence needed to resolve it are tracked in the table above; the search procedure itself remains canonical in [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing).

**Working project direction (partly open):** an agreement is the established arrangement between the client pool and the servicing pool, and its protocol terms are expressed by the transaction type. The transaction type is not a separate compatibility mechanism. Dependent types may express details specific to a particular agreement, but the exact meaning of those details and their role in matching versus agreement-specific instantiation remain open. **Agreed project decisions:** automatic search looks among previously established agreements. If it finds no suitable agreement, manual intervention always follows; a participant of the calling pool can select a candidate pool to begin negotiating a new agreement. A pool may participate in multiple previously established agreements. If automatic search finds multiple suitable agreements, a selection order exists, but its rules remain open. **Agreed project decision:** the agreement-search timeout belongs to the search mechanism, not to the transaction type. Expiry therefore indicates that this search has terminated under its time limit; it does not by itself establish that the candidate types are incompatible or that no suitable agreement exists. The timeout's operational boundary is specified in [Process creation and pool selection, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). The calling pool supplies one shared timeout setting for all agreement searches initiated by calls from that pool. Its configuration interface, representation, and valid range remain open.

## 5. The pool's public transaction channel

**Inferred:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public transaction channel. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Project semantic decision on public/private state and identity levels:** from the client's perspective, there is one logical channel placeholder whose state changes over the course of the protocol: it is public, becomes private, and later becomes public again. Public and private are not two independently existing logical channels. The physical identity depends on the state: before `Up`, the client uses the pool's original public channel identity; when `acquire` and `accept` match, both participants' continuations use a new private channel identity; when `release` and `detach` match, the client returns to the original public channel identity, not a newly allocated public identity. Thus the logical placeholder is continuous, the private phase has its own physical channel identity, and `Down` restores the original public identity.

The type-level constructors describe the permitted state transitions. `Up` describes the transition from public to private; `Down` describes the transition from private back to public. These constructors are not runtime interaction operations. At the interaction level, the client performs `acquire` and the provider performs `accept`; the public-to-private transition takes effect when those operations match. Conversely, the client performs `release` and the provider performs `detach`; the private-to-public transition takes effect when those operations match. The terminal `One` interaction (`close`/`wait`) is separate from this pool-level public/private lifecycle: its shared channel-identity rule does not represent entry into or return from a private phase.

What happens next after the return to public state depends on the participant-specific `ContExp` values carried by `detach` and `release`. They are checked against the provider-side continuation type `A` and the corresponding client-side protocol type, respectively. Returning to the public state does not, by itself, guarantee that another `Up` happens immediately, nor does it imply that the pool must perform an additional action first. The continuations determine each participant's next permitted behavior.

The state transition does not by itself imply resource destruction, recycling, pool-state changes, or process termination. The precise resource disposition and the operational representation of the channel's changing access state remain open.

This pool-level protocol is conceptually distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Process creation and pool selection](../about-spawn/README.md).

## 6. Intended semantics and formal rules

This section records the agreed minimal language-level decisions for matching and continuation behavior, while leaving a complete operational semantics unfinished. The decisions below specify when the protocol transition counts as occurring; they do not establish implementation correctness, complete typing rules, failure semantics, or every state transition.

### 6.1 Minimal transaction-type constructors

**Status: Project semantic decisions, with formalization still open.** The matching points, shared channel-identity rules, and participant-specific continuation obligations recorded below are adopted language-level requirements. Their complete typing judgments, operational rules, and implementation conformance are not yet established; this research document is not itself the normative language specification.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A client's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared client-side transaction type is required by this model.

| Constructor | Provider-side operation | Client-side operation | Minimal intended meaning | Further detail |
|---|---|---|---|---|
| `One` | `close` | `wait` | Terminal provider interaction and corresponding client wait. The client's enclosing expression may continue after `wait`; provider-side `close` has no executable continuation of its own. | Matching and shared-identity rule: Section 8. `One` does not itself imply process termination. |
| `Up A` | `accept` | `acquire` | Provider accepts access; client acquires access. | Matching, private identity, and participant continuation rules: Section 8. Formal typing remains open; `dual(A)` is provisional explanatory notation only. |
| `Down A` | `detach` | `release` | Provider detaches access; client releases access. | Matching, restoration of the original public identity, and mandatory participant-specific `ContExp` on both operations: Section 8. Formal typing and resource disposition remain open. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/client operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

#### Continuation correspondence: dual endpoint views

**Decision recorded from semantic review:** `A` describes the provider-side continuation protocol; the client-side continuation must be checked against the corresponding client-side protocol type. For brevity, this document uses `dual(A)` as a provisional notation for that client-side type. This notation is introduced here for explanatory purposes only: it is not an established OrgLang grammar constructor or operation, and no definition or derivation rule for it is assumed. The participant-specific continuation expressions need not be textually identical, but each must satisfy the typing obligation for its own endpoint. Matching the operation pair and binding the appropriate shared channel identity do not, by themselves, make arbitrary `ContExp` values valid.

This decision establishes the intended endpoint relationship, not the complete typing judgment. The formal representation of the client-side type, the typing rules, and how the continuation channel identity is substituted into each participant's continuation remain to be specified and tested.

#### Formalization obligations

Section 8 records the adopted matching and continuation behavior. To complete its formal specification, specify for each paired operation:

- **Precondition:** the current protocol state, participant roles, and any agreement/access prerequisites.
- **Action and matching:** which operation enables or matches the peer operation, and whether matching is atomic or has observable intermediate states.
- **Result:** the next protocol state and the continuation/channel identity available to each participant.
- **Failure boundary:** what happens when the peer operation is absent or the protocol state does not permit the operation. Error recovery and retries remain outside this initial proposal unless they affect safety.
- **Evidence:** the language-level rule, then implementation-path and observable-test evidence for conformance.

#### Initial conformance examples

These examples translate the decisions in Section 8 into acceptance criteria for future tests; they are not claims that tests already exist or pass:

1. **`One`:** a client waiting for the provider's `close` may proceed to its own continuation only after the close/wait pair matches; matching establishes one channel identity shared by both sides. The close interaction does not itself terminate the enclosing client process.
2. **`Up`:** a client cannot treat access as acquired unless the provider-side protocol permits and matches the acquisition; both participants continue according to the continuation associated with `Up`.
3. **`Down`:** after a valid detach/release match, the current access cannot be treated as still active, and the match establishes one channel identity shared by both sides. The test must not assume resource destruction, reuse, or process termination unless a separate lifecycle rule specifies it.
4. **Protocol conformance:** an operation that contradicts the current provider-side protocol state is rejected or otherwise prevented according to a separately specified checking/enforcement rule; that enforcement mechanism is currently open.

For each rule adopted in this section, record:

1. **Preconditions:** the participant roles, channel/type state, and any agreement or resource prerequisites.
2. **Action:** which participant sends, receives, selects, or applies a continuation.
3. **Result:** the next protocol state, the identity and ownership of any channel/resource, and any change to pool state.
4. **Observable state at a transition boundary:** where relevant, state the pre-state/post-state and ordering constraints needed to preserve protocol and resource invariants. Detailed error reporting, recovery, retries, and abnormal-termination semantics are outside this specification pass.
5. **Evidence:** the source for the intended language rule, plus separate implementation-path/test evidence where conformance is claimed.

Until these points are settled, keep only the corresponding unresolved detail explicitly **Open** and link to the relevant question in Section 9. Do not downgrade the adopted matching, identity, or continuation requirements recorded in Section 8.1.

## 7. Publication correspondence

The [transaction introduction](../about-transaction/README.md) contains a formal model and a transaction-type table. Its Table 4 says that `↑ A` sends a `grant` token and continues as `A`, while `↓ A` accepts a `revoke` token and continues as `A`. The continuation grammar and application rules (Tables 2 and the definition of `V ▷ K`) explain how a received value selects a continuation and substitutes an identifier for a placeholder.

This establishes that the publication model associates `↑ A` and `↓ A` with continuation behavior at the type level. The OrgLang language-level operation model additionally requires each side of `Down`—provider-side `detach` and client-side `release`—to carry its own participant-specific `ContExp`. These expressions need not be identical: the provider continuation is checked against `A`, and the client continuation against the corresponding client-side protocol type. This is a language-level requirement, not a claim that the current runtime operation structs already expose those fields. The publication table's send/accept wording also should not be equated mechanically with the current runtime operation names (`accept`/`acquire`, `detach`/`release`) without an explicit role and polarity mapping.

### Initial constructor/role correspondence table

The table below separates the publication model's token polarity from OrgLang's current provider/client operation names. It is a working correspondence, not a claim that the runtime implementation already conforms.

| Type constructor | Publication-level action | Provider-side OrgLang operation | Client-side OrgLang operation | Established minimum | Still open |
|---|---|---|---|---|---|
| `One` (`𝟏`) | The provider-side type sends `close`; the client-side dual action receives/waits for it. | `close` | `wait` | The pair must match before the interaction counts as complete; matching establishes one shared channel identity. The client's enclosing expression may continue after `wait`; provider-side `close` is terminal for this interaction and has no executable continuation of its own. | The precise correspondence between the publication's terminal `close` case and OrgLang's enclosing-expression behavior, plus the formal typing of the shared identity for this terminal case. |
| `Up A` (`↑ A`) | The provider-side type sends `grant`, then continues as `A`; the client performs the complementary receive/acquire action. | `accept` | `acquire` | Access starts only when the pair matches; both participants use the shared new private channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, plus formal typing judgments and runtime conformance. |
| `Down A` (`↓ A`) | The provider-side type accepts/receives `revoke`, then continues as `A`; the client performs the complementary send/release action. | `detach` | `release` | Access ends only when the pair matches; both operations must carry their own participant-specific `ContExp`. After matching, each continuation may proceed with the restored original public channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, formal typing judgments, and runtime conformance. |

**Polarity rule for this comparison:** the transaction type is the protocol exposed by the provider. Therefore its publication-level action is read from the provider endpoint: `↑ A` sends `grant`, while `↓ A` receives `revoke`. The client endpoint performs the complementary action. This polarity follows the type table's send/accept wording together with the document's statement that the pool provides a transaction of type `A`; it is a model-level reading, not proof of the exact runtime implementation. The runtime names `accept`, `acquire`, `detach`, and `release` must still be checked against their code paths and tests, not matched by English verb similarity alone.

The initial comparison should cover:
- the grammar and reduction/application operation for values, continuations, and pool terms;
- the transaction-type constructors and their side conditions;
- the relationship between a type's constraints and the pool-state set used by the model;
- the spawn-form rule and its relationship, if any, to OrgLang's `SpawnSpec`.

**Open:** whether these publication constructs correspond one-to-one to OrgLang constructs. Similar names or matching notation are not sufficient evidence.

## 8. Implementation evidence

Implementation conformance has not been established by this document. The following are **implementation observations only** from the inspected source snapshot; they do not establish that the language contract must have identical semantics.

| Path / symbol | Observed behavior | What this establishes | What remains unverified |
|---|---|---|---|
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `AcceptSpec` and `AcquireSpec` | If `commSnap.NextTurn()` is empty, the executor records a `SubRec` containing the operation and continuation, logs `taking half done`, and returns without binding either continuation. When the matching opposite operation is already registered, it creates one new channel ID, binds both participants' continuation channels to it, advances the exchange offset, and schedules non-nil continuations. | The inspected implementation permits a first-arriving operation to remain pending and performs continuation binding when the opposite operation is matched. | Whether the pending registration is externally observable, the intended atomicity/linearization point, cancellation/interleaving behavior, and whether this path is complete for all runtime cases. |
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `DetachSpec` and `ReleaseSpec` | The same pending-subscription pattern is used. On matching, the implementation creates a channel ID and binds both continuation channels; these cases do not schedule participant-specific `ContExp` expressions. The bound runtime continuation channels should not be confused with the language-level `ContExp` expressions required on both operations. The inspected code path alone does not establish how this ID relates to the original public channel identity at the language level. | The current implementation models `detach`/`release` as a paired interaction with a continuation channel after matching. | Resource disposition after the interaction and any broader lifecycle contract. |
| [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go) and [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go), operation-spec declarations | In both packages, `DetachSpec` and `ReleaseSpec` contain only `CommChnlPH`; neither declares a `ContExp` field. By contrast, `AcceptSpec` and `AcquireSpec` declare `ContExp`. In the process package, `CloseSpec` has no `ContExp`, while `WaitSpec` does. | The inspected runtime operation-spec structures do **not** satisfy the language-level `Down` requirement recorded here: both `detach` and `release` must carry participant-specific `ContExp` values. `Up` already has continuation fields on both operations. | The runtime AST/specs, typing, adapters, executor, and tests must be brought into alignment with the `Down` contract. This is a documented conformance gap, not a reason to weaken the language-level requirement. |
| [`proc/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go), `takeWith` cases for `CloseSpec` and `WaitSpec` | If no opposite operation is registered, the executor records a pending subscription and returns. On matching `close`/`wait`, it creates a new channel ID and binds both sides to the `One` continuation type; the wait-side continuation is scheduled when non-nil. | The inspected process executor uses the same pending-then-match pattern for `One`. | Whether the language contract requires this exact scheduling/observability behavior, and abnormal termination/error behavior. |
| [`pool/termexp/adapter/tc.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/adapter/tc.go) | The adapter maps the core operation specifications to SDK operation variants with corresponding names. | The operation names are carried through the adapter. | An adapter mapping alone does not establish protocol correctness or type conformance. |
| [`test/e2e/pool_test.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go), `TestPool` / `waitClose` | The test builds an `Up`/`With`/`Down` pool type and exercises some pool acquisition/acceptance steps. The `close`/`wait` process interaction and final outcome assertion are commented out; the test contains a TODO for an assertion. | This file provides an example of intended test setup and partial execution coverage. | It does not currently establish an asserted end-to-end `One` outcome or full conformance for `Up`/`Down`. The test was inspected, not run in this task. |

These paths suggest that the implementation has a **pending registration** stage followed by a **matching/continuation-binding** stage. In the inspected `detach`/`release` path, the executor creates a channel ID and binds runtime continuation channels, but does not schedule participant-specific `ContExp` expressions (and the operation specs do not expose those fields). Runtime continuation-channel binding is distinct from the language-level continuation expressions required on both operations. This source-level observation does not tell us how that ID maps to the logical channel placeholder or to the original public identity described by the language-level model. The internal mechanism for preserving and restoring that identity is an implementation detail and is not specified here. Do not call the whole interaction atomic without defining the relevant observable boundary: the database mutation and broker scheduling path, and concurrent interleavings, would need to be traced to settle that question.

The [`TestPool` / `waitClose` example](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go) defines the type-level continuation as `Down { ContExp: Link{TypeQN: poolTypeQN} }`, but its runtime `ReleaseSpec` and `DetachSpec` literals supply only `CommChnlPH`. This is consistent with the operation-spec declarations above and exposes the same implementation gap: the example does not encode the two required participant-specific `ContExp` values. The test's final `close`/`wait` sequence and outcome assertion are commented out, so it is partial evidence only; it does not validate the complete lifecycle.

### 8.1 Adopted language-level matching rules

The language-level transition for each constructor occurs only when its provider-side and client-side operations match:

- **`Up`:** provider `accept` matches client `acquire`; access becomes active and both participants receive the same new private channel identity.
- **`Down`:** provider `detach` matches client `release`; access ends and both participants regain the original public channel identity.
- **`One`:** provider `close` matches client `wait`; the transaction interaction completes and matching establishes one shared channel identity. This is separate from the `Up`/`Down` public/private identity cycle.

### 8.2 Matching boundary and continuation behavior

**Common matching rule:** registering only one side of any operation pair creates a pending operation. It does not itself change the publicly observable protocol state: access remains inactive before a matched `Up`, remains active before a matched `Down`, and `One` remains incomplete before a matched `close`/`wait`. The language-level transition occurs when the corresponding operations match.

**Continuation rules after matching:**

- For `Up A`, both provider `accept` and client `acquire` carry their own participant-specific continuation expressions. They need not be textually identical, and neither executes before the operations match. After matching, each participant may proceed through its own continuation using the shared new private channel identity. The provider continuation is checked against `A`; the client continuation is checked against its corresponding client-side protocol type (provisionally denoted `dual(A)`).
- For `Down A`, both `detach` and `release` must carry their own participant-specific continuation expressions (`ContExp`); they need not be textually identical. Neither executes before matching. After matching, each participant may proceed independently through its own continuation using the restored original public channel identity. The provider continuation is checked against `A`, and the client continuation against its corresponding client-side protocol type (provisionally denoted `dual(A)`).
- For `One`, the client's `wait` may continue in its enclosing expression; provider-side `close` is terminal for this interaction and has no executable continuation of its own.

Matching establishes one physical channel identity shared by both sides, not two independent identities. For `Up` this is the new private identity; for `Down` it is the restored original public identity. The logical placeholder remains continuous across the public/private transitions described in Section 5. `One` has its separate shared-identity rule and is not part of that cycle. Matching imposes no additional ordering between continuations that exist and does not guarantee simultaneous execution.

These are language-level semantic decisions, not a claim that every implementation interleaving has been verified. The exact implementation linearization point, cancellation/failure behavior, and other abnormal interleavings remain open; cancellation semantics are explicitly deferred.

This is a language-level design decision; it does not claim that the current `go-engine` operation specs already expose these continuation fields. The next implementation work, if authorized, should align the AST/operation model, typing, adapters, executor, and tests with this decision. Absence from the paths above does not establish system-wide absence.

## 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| Which transaction-type constructors and syntax are part of OrgLang, rather than only the companion model? | Grammar, type checking, and compatibility of programs. | Adopted grammar/project decision; compare parser and type-checker support separately. |
| What formal rules remain for `One`, `Up`, and `Down`? | Matching points, shared-identity rules, and the requirement for participant-specific `ContExp` on both `Down` operations are decided. Formal typing, type-state progression, ownership, and observable boundaries remain open. | Define the typing and state-transition judgments; add positive and negative tests without reopening the adopted decisions. |
| How is continuation typing formalized? | **Decision:** the provider-side continuation is checked against `A`, and the client-side continuation against the corresponding client-side protocol type, provisionally denoted `dual(A)`. This notation is not an established grammar construct. The formal judgments and channel-identity substitution remain open. | Define the typing judgments and client-side protocol type representation; test valid and invalid continuation pairs, including channel-identity substitution. |
| How do the publication's continuation notation and actions map to OrgLang's participant-specific continuations and runtime operations? | The OrgLang endpoint obligations are adopted; the correspondence between the publication's notation/actions and OrgLang's runtime operations remains open. | Verify provider/client polarity and action correspondence against language rules and runtime paths; do not infer runtime semantics from publication wording alone. |
| What is the lifecycle of the private physical channel resource after `Down`? | Whether the resource is destroyed, recycled, or retained after the matched `detach`/`release` transition restores the original public channel identity. | Specify resource disposal/reuse separately from the already-decided logical identity, public-state transition, and participant-specific continuation requirements. |
| How do cancellation, failure, and concurrency affect pending or matching `Up`/`Down` interactions? | Whether a pending participant can withdraw, how peer absence or failure is handled, and which interleavings are permitted around a matched transition. | Specify cancellation and failure semantics without weakening the adopted rule that the public protocol transition occurs only when the corresponding operations match; add interleaving and peer-absence tests. |
| Can individual processes expose public transaction channels, or is this pool-only? | Public API and which entity owns the public protocol endpoint. | Project decision grounded in language examples or source rules; inspect implementation only as conformance evidence. |
| Which agreement-specific details, if any, supplement the agreed process-name match when determining suitability? | The process-name match is the current agreed criterion; whether dependent type details further constrain suitability remains open. | Define the role of dependent type details and add positive and negative examples, consistently with [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing). |
| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |
