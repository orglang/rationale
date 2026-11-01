<!-- Canonical semantics: pool and transaction-type model; process/pool selection remains in ../about-matching-and-spawn/README.md -->

# Pools and transaction types

> **Status: preliminary semantic research.** This document is a technical companion to [What is a transaction?](../about-transaction/README.md). It collects the language-level model of pools and transaction types, distinguishes intended semantics from publication rules and implementation observations, and records unresolved questions. Its conclusions remain research findings pending a normative specification.

**Scope and document boundaries**

- This document owns the technical model of pools and transaction types, including the pool's public transaction channel and its protocol.
- [Matching and spawn](../about-matching-and-spawn/README.md) owns pool eligibility, search order, process-incarnation creation, pool binding, and the start of servicing.
- [What is a transaction?](../about-transaction/README.md) provides the accessible introduction.
- [Processes and session types](../about-processes-and-session-types/README.md) owns process expressions and the intended semantics of `ExternalCall` and `InternalCall`.

## 1. Scope, evidence, and status

This research draft keeps language-level intended semantics, claims made by the supplied publication, and implementation observations separate. A normative language specification remains future work.

Use the claim-status vocabulary from [Processes and session types, Section 1](../about-processes-and-session-types/README.md#1-scope-and-evidence): **Confirmed**, **Inferred**, and **Open**. Record the source and what it establishes for substantial or disputed claims. Implementation coverage is a separate dimension and should be recorded only when the relevant code path or test has been inspected.

## 2. Core concepts and terminology

The following working definitions are inferred from the current model described in [What is a transaction?](../about-transaction/README.md).

| Term | Working meaning | Status and limitation |
|---|---|---|
| Pool | A participant that can communicate with other pools and may service a process incarnation under an agreement. | **Inferred** from the explanatory model and the current process–pool model. Pool lifecycle, internal state, and whether every incarnation must always be bound to one pool remain **Open**. |
| Pool term | An executable expression describing a pool's communication or state transition. | **Inferred** from the companion model's distinction between terms, values, and continuations. Its runtime representation in OrgLang is **Open**. |
| Transaction channel | One shared pool-to-pool channel through which a consumer pool interacts with a provider pool to establish or modify an agreement. Each pool has its own endpoint of that same channel. | **Inferred** from the current model discussion. The common endpoint and matching principle is described in [Matching and spawn](../about-matching-and-spawn/README.md#common-matching-principle); lifecycle and failure rules remain **Open**. |
| Agreement | The allocation state `Q_c` of the shared transaction channel `c`, established by a consumer pool and a provider pool through interaction governed by a transaction type. Each provider/consumer pair may have distinct agreements on distinct channels. | **Agreed working model:** `Q_c` is the complete agreement state for channel `c`. Its formal representation and lifecycle remain to be specified. |
| Transaction identifier | An identifier used to refer to a transaction or its channel in the pool model. | **Inferred**. Its concrete representation, allocation/uniqueness guarantees, and exact referent are **Open**; it identifies a pool transaction or its channel. |
| Transaction type | The protocol by which pools interact to establish and modify the channel-local agreement state `Q_c`; it governs which negotiation messages and transitions are permitted. Its dependent state index records the current allocation map. | **Inferred** from the companion model's transaction-type grammar and current project direction. Exact OrgLang syntax, checking rules, and runtime enforcement remain **Open**. |
| Provider/consumer endpoint roles | The provider and consumer own their respective endpoints of one shared transaction channel. | **Agreed project decision** for endpoint ownership; lifecycle and failure rules remain **Open**. |
| Process provider channel | The channel on which a process incarnation provides its named-process service. | Defined in [Processes and session types, Section 2](../about-processes-and-session-types/README.md#2-core-concepts). It is distinct from the pool's public transaction channel. |

A transaction identifier and a process channel identity refer to distinct resources. Their precise mapping remains **Open** pending evidence from the language contract or a verified execution path.

A **transaction** is the pool-to-pool interaction; its **transaction type** is the governing protocol; the **agreement** is the channel state established or modified through that interaction. A **transaction identifier** refers to the transaction or its channel. Its relation to agreement identity remains **Open**.

## 2.1 Negotiation protocol and established agreement

The current model has three related concepts:

1. **Transaction type:** the protocol that governs how pools interact while establishing or modifying an agreement. It describes permitted messages, choices, constraints, and continuations.
2. **Negotiation interaction:** the pool-to-pool exchange governed by that protocol. Its precise channel representation remains unspecified.
3. **Agreement:** the complete allocation map `Q_c` for the shared transaction channel `c`, accepted by the participating pools. Once established, this state can be found and reused by a later `ExternalCall`; finding it is distinct from negotiating or modifying it.

For the discovery and negotiation sequence, including the point at which incarnation creation may begin, see [Matching and spawn, Sections 4.3–4.4](../about-matching-and-spawn/README.md#43-search-and-agreement-negotiation).

### What the formal transaction-type model establishes

The grammar in the [transaction introduction](../about-transaction/README.md) gives evidence for a **state-indexed protocol**:

- The type constructors describe interactions such as `grant`, `revoke`, `choice`, `coop`, `isol`, and `spawn`.
- The `Coop` and `Isol` constructors carry the state `Q` of the particular transaction channel and produce an updated state `Q'`; the continuation is indexed by that updated state.
- The spawn constructor requires positive allocation weight for the named process on that channel: `Q_c(q) > 0`; its continuation retains the stated `Q`.
- The type grammar also places a continuation `A` after these state constraints and transitions.

`Q_c` is the allocation map associated with transaction channel `c`. Its interpretation and transition rules are defined canonically in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения). The map is maintained per channel and describes the provider's allocation offered through that channel.

**Agreed working model:** `Q_c` is the complete agreement state for transaction channel `c`. The dependent part of the transaction type indexes this state; there are no additional agreement terms in the current model. The formal representation of the negotiation result and the lifecycle of the established state remain to be specified.

### Agreement lifecycle: current contract and missing rules

| Stage | Current project contract | Still unspecified |
|---|---|---|
| Existing-agreement discovery | Search established channel agreements for one whose `Q_c(q) > 0` for the called process `q`. | Storage and indexing, visibility/ownership, concurrency with agreement changes, and selection among multiple suitable agreements. |
| Candidate selection | If discovery finds none, manual intervention selects a candidate pool. Selection does not itself establish an agreement. | Authorization, candidate presentation, and whether candidates can be rejected before negotiation starts. |
| Negotiation | The candidate pools interact according to the applicable transaction type. A failed candidate may be replaced before the shared timeout expires. | The exact message sequence, who proposes and accepts each term, how partial progress is rolled back, and what constitutes successful agreement. |
| Establishment | Successful negotiation yields a new agreement that can be used by the call and potentially discovered by later calls. | The atomic commit point, durable representation, identity/versioning, scope, lifetime, revocation, and whether both pools record it simultaneously. |
| Service activation | Only after a suitable existing agreement is found or a new one is successfully established does the engine create the incarnation and deliver the provider channel. | Resource reservation/consumption semantics and failure handling between agreement establishment and channel delivery. |

**Agreement establishment** concludes pool-level negotiation. **Service activation** is the subsequent engine operation that creates and connects a process incarnation. A specification should identify the agreement's commit point before defining retries, timeout boundaries, or recovery from a failure during activation.

### Questions required to complete the agreement model

- How is the established `Q_c` state represented and committed as the result of successful negotiation, and how is that result associated with the transaction channel?
- Which parts of the transaction type describe the negotiation protocol, and how does its dependent state index the resulting `Q_c`?
- What operation or judgment distinguishes a negotiation that is still in progress from one whose agreement has been accepted by both parties?
- What makes an established agreement reusable, and how are updates, revocation, or replacement observed by concurrent `ExternalCall` searches?



## 3. Pool model

**Inferred working model:** a pool is represented by a pool term/state and exposes a public transaction channel through which other pools interact according to a transaction type. The provider/consumer endpoints and matching principle are defined in [Matching and spawn](../about-matching-and-spawn/README.md#common-matching-principle); the channel-local allocation map is defined in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения). The process's provider channel is a distinct resource. Pool lifecycle and behavior when a pool cannot service a request remain **Open**.

## 4. Transaction types

The companion [transaction introduction](../about-transaction/README.md) presents the candidate transaction-type grammar, including termination, directional `Up` and `Down`, choice, `Coop`, `Isol`, and process spawning. The formal representation and transitions of the per-channel allocation map `Q` are defined there; this document focuses on pool roles, negotiation, and agreements.

| Question | Current status | Why it matters | Evidence needed |
|---|---|---|---|
| Which constructors belong to the OrgLang transaction-type language, and what is their exact syntax? | **Open** | Determines what specifications and programs may express. | An adopted language grammar or an explicit project decision; compare with the companion model and implementation parser/type definitions. |
| What are the remaining exact transition rules for `One`, `Up`, and `Down`, including type-state progression, ownership, and observable boundaries? | **Partly decided; partly Open** | Matching is the transition point; the remaining state progression and observability details govern conformance. | Preserve the adopted decisions in Section 6.2; specify remaining obligations, then test permitted and prohibited transitions. |
| Are constraints on pool state part of type checking, runtime validation, or both? | **Open** | Determines which constraints expressed by the transaction-type agreement are checked statically and which require runtime validation. | A typing/validation rule and implementation-path evidence, with negative examples. |


### Per-channel allocation state

The transaction-type grammar is state-indexed: `Coop` and `Isol` transition the allocation map associated with the shared transaction channel, while `spawn` requires a positive allocation weight for the requested process. The canonical definition of the map, its initialization, allocation weights, and transition side conditions are in [What is a transaction?](../about-transaction/README.md#типы-ограничения-уточнения).

The map `Q_c` is the complete agreement state and belongs to the provider's channel resource, not to the consumer pool globally. A pool may participate in multiple agreements concerning the same process name on different channels. No cross-channel summation rule is currently imposed.

A pool may participate in multiple established agreements concerning the same process name, including agreements on different transaction channels. The order for selecting among multiple suitable agreements remains **Open**; the discovery and negotiation procedure is specified in [Matching and spawn, Sections 4.3–4.5](../about-matching-and-spawn/README.md#43-search-and-agreement-negotiation).

## 5. The pool's public transaction channel

**Inferred:** the pool's public transaction channel is part of the current explanatory pool model. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel is described by a transaction type. The two participating pools use one shared channel through their respective endpoints: the provider pool uses its provider endpoint, and the consumer pool uses its consumer endpoint. The channel's agreement state `Q_c` is initialized from the provider pool's declared competencies. The exact matching points, participant continuations, and channel-identity rules are specified canonically in [Matching and spawn](../about-matching-and-spawn/README.md#common-matching-principle) and [Section 6.2](#62-matched-transitions-continuations-and-channel-identity); this section does not restate those rules.

The public/private protocol transition does not by itself imply resource destruction, recycling, pool-state changes, or process termination. The precise resource disposition and the operational representation of the channel's changing access state remain open.

This pool-level protocol is conceptually distinct from a process's provider channel and from channels mapped to a new incarnation's consumer-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Matching and spawn](../about-matching-and-spawn/README.md).

## 6. Intended semantics and formal rules

This section records the agreed minimal language-level decisions for matching and continuation behavior, while leaving a complete operational semantics unfinished. The decisions below specify when the protocol transition counts as occurring; they do not establish implementation correctness, complete typing rules, failure semantics, or every state transition.

### 6.1 Minimal transaction-type constructors

**Status: Project semantic decisions, with formalization still open.** The matching points, shared channel-identity rules, and participant-specific continuation obligations recorded below are adopted language-level requirements. Their complete typing judgments, operational rules, and implementation conformance are not yet established; this research document is not itself the normative language specification.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A consumer's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared consumer-side transaction type is required by this model.

| Constructor | Provider-side operation | Consumer-side operation | Minimal intended meaning | Further detail |
|---|---|---|---|---|
| `One` | `close` | `wait` | Terminal provider interaction and corresponding consumer wait. The consumer's enclosing expression may continue after `wait`; provider-side `close` has no executable continuation of its own. | Matching and shared-identity rule: Section 6.2. `One` does not itself imply process termination. |
| `Up A` | `accept` | `acquire` | Provider accepts access; consumer acquires access. | Matching, private identity, and participant continuation rules: Section 6.2. Formal typing remains open; `dual(A)` is provisional explanatory notation only. |
| `Down A` | `detach` | `release` | Provider detaches access; consumer releases access. | Matching, restoration of the original public identity, and mandatory participant-specific `ContExp` on both operations: Section 6.2. Formal typing and resource disposition remain open. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/consumer operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

### 6.2 Matched transitions, continuations, and channel identity

The general paired-interaction principle is defined in [Matching, process creation, and pool selection](../about-matching-and-spawn/README.md#common-matching-principle). This section specifies its pool-specific consequences:

- **`One`:** provider `close` matches consumer `wait`. Only the matched pair completes the transaction interaction and establishes one channel identity shared by both sides. Consumer-side `wait` may continue in its enclosing expression; provider-side `close` is terminal and has no executable continuation of its own.
- **`Up A`:** provider `accept` matches consumer `acquire`. Access becomes active and both participants receive the same new private physical channel identity.
- **`Down A`:** provider `detach` matches consumer `release`. Access ends and both participants regain the original public physical channel identity.

For `Up A`, both `accept` and `acquire` carry their own participant-specific continuation expressions. They need not be textually identical, and neither executes before matching. After matching, each participant may proceed through its own continuation using the shared new private identity. The provider continuation is checked against `A`; the consumer continuation against its corresponding consumer-side protocol type (provisionally denoted `dual(A)`).

For `Down A`, both `detach` and `release` must carry their own participant-specific `ContExp` values. They need not be textually identical, and neither executes before matching. After matching, each participant may proceed independently through its own continuation using the restored original public identity. The provider continuation is checked against `A`; the consumer continuation against its corresponding consumer-side protocol type (provisionally denoted `dual(A)`).

The logical channel placeholder remains continuous across the public/private transitions: the original public physical identity is replaced by the shared private identity on matched `Up` and restored on matched `Down`. The mechanism that preserves and restores the original identity is an implementation detail. `One` has its separate shared-identity rule and is not part of this public/private cycle. Matching imposes no additional ordering between participant continuations and does not guarantee simultaneous execution.

#### Continuation correspondence: dual endpoint views

**Decision recorded from semantic review:** `A` describes the provider-side continuation protocol; the consumer-side continuation must be checked against the corresponding consumer-side protocol type. For brevity, this document uses `dual(A)` as a provisional notation for that consumer-side type. This notation is introduced here for explanatory purposes only: it is not an established OrgLang grammar constructor or operation, and no definition or derivation rule for it is assumed. The participant-specific continuation expressions need not be textually identical, but each must satisfy the typing obligation for its own endpoint. Matching the operation pair and binding the appropriate shared channel identity do not, by themselves, make arbitrary `ContExp` values valid.

This decision establishes the intended endpoint relationship, not the complete typing judgment. The formal representation of the consumer-side type, the typing rules, and how the continuation channel identity is substituted into each participant's continuation remain to be specified and tested.

#### Initial conformance examples

These examples translate the decisions in Section 6.2 into acceptance criteria for future tests; they are not claims that tests already exist or pass:

1. **`One`:** a consumer waiting for the provider's `close` may proceed to its own continuation only after the close/wait pair matches; matching establishes one channel identity shared by both sides. The close interaction does not itself terminate the enclosing consumer process.
2. **`Up`:** a consumer cannot treat access as acquired unless the provider-side protocol permits and matches the acquisition; both participants continue according to the continuation associated with `Up`.
3. **`Down`:** after a valid detach/release match, the current access cannot be treated as still active, and the match establishes one channel identity shared by both sides. The test must not assume resource destruction, reuse, or process termination unless a separate lifecycle rule specifies it.
4. **Protocol conformance:** an operation that contradicts the current provider-side protocol state is rejected or otherwise prevented according to a separately specified checking/enforcement rule; that enforcement mechanism is currently open.

For each rule adopted in this section, record:

1. **Preconditions:** the participant roles, channel/type state, and any agreement or resource prerequisites.
2. **Action:** which participant sends, receives, selects, or applies a continuation.
3. **Result:** the next protocol state, the identity and ownership of any channel/resource, and any change to pool state.
4. **Observable state at a transition boundary:** where relevant, state the pre-state/post-state and ordering constraints needed to preserve protocol and resource invariants. Detailed error reporting, recovery, retries, and abnormal-termination semantics are outside this specification pass.
5. **Evidence:** the source for the intended language rule, plus separate implementation-path/test evidence where conformance is claimed.

Until these points are settled, keep only the corresponding unresolved detail explicitly **Open** and link to the relevant question in Section 9. Do not downgrade the adopted matching, identity, or continuation requirements recorded in Section 6.2.

## 7. Publication correspondence

The [transaction introduction](../about-transaction/README.md) contains a formal model and a transaction-type table. Its Table 4 says that `↑ A` sends a `grant` token and continues as `A`, while `↓ A` accepts a `revoke` token and continues as `A`. The continuation grammar and application rules (Tables 2 and the definition of `V ▷ K`) explain how a received value selects a continuation and substitutes an identifier for a placeholder.

This establishes that the publication model associates `↑ A` and `↓ A` with continuation behavior at the type level. The OrgLang language-level operation model additionally requires each side of `Down`—provider-side `detach` and consumer-side `release`—to carry its own participant-specific `ContExp`. These expressions need not be identical: the provider continuation is checked against `A`, and the consumer continuation against the corresponding consumer-side protocol type. This is a language-level requirement, not a claim that the current runtime operation structs already expose those fields. The publication table's send/accept wording also should not be equated mechanically with the current runtime operation names (`accept`/`acquire`, `detach`/`release`) without an explicit role and polarity mapping.

### Initial constructor/role correspondence table

The table below separates the publication model's token polarity from OrgLang's current provider/consumer operation names. It is a working correspondence, not a claim that the runtime implementation already conforms.

| Type constructor | Publication-level action | Provider-side OrgLang operation | Consumer-side OrgLang operation | Established minimum | Still open |
|---|---|---|---|---|---|
| `One` (`𝟏`) | The provider-side type sends `close`; the consumer-side dual action receives/waits for it. | `close` | `wait` | The pair must match before the interaction counts as complete; matching establishes one shared channel identity. The consumer's enclosing expression may continue after `wait`; provider-side `close` is terminal for this interaction and has no executable continuation of its own. | The precise correspondence between the publication's terminal `close` case and OrgLang's enclosing-expression behavior, plus the formal typing of the shared identity for this terminal case. |
| `Up A` (`↑ A`) | The provider-side type sends `grant`, then continues as `A`; the consumer performs the complementary receive/acquire action. | `accept` | `acquire` | Access starts only when the pair matches; both participants use the shared new private channel identity. The provider continuation is checked against `A`, and the consumer continuation against its corresponding consumer-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, plus formal typing judgments and runtime conformance. |
| `Down A` (`↓ A`) | The provider-side type accepts/receives `revoke`, then continues as `A`; the consumer performs the complementary send/release action. | `detach` | `release` | Access ends only when the pair matches; both operations must carry their own participant-specific `ContExp`. After matching, each continuation may proceed with the restored original public channel identity. The provider continuation is checked against `A`, and the consumer continuation against its corresponding consumer-side protocol type (provisionally `dual(A)`). | The exact correspondence between the publication's actions and OrgLang's runtime operations, formal typing judgments, and runtime conformance. |

**Polarity rule for this comparison:** the transaction type is the protocol exposed by the provider. Therefore its publication-level action is read from the provider endpoint: `↑ A` sends `grant`, while `↓ A` receives `revoke`. The consumer endpoint performs the complementary action. This polarity follows the type table's send/accept wording together with the document's statement that the pool provides a transaction of type `A`; it is a model-level reading, not proof of the exact runtime implementation. The runtime names `accept`, `acquire`, `detach`, and `release` must still be checked against their code paths and tests, not matched by English verb similarity alone.

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

## 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| Which transaction-type constructors and syntax are part of OrgLang, rather than only the companion model? | Grammar, type checking, and compatibility of programs. | Adopted grammar/project decision; compare parser and type-checker support separately. |
| What formal rules remain for `One`, `Up`, and `Down`? | Matching points, shared-identity rules, and the requirement for participant-specific `ContExp` on both `Down` operations are decided. Formal typing, type-state progression, ownership, and observable boundaries remain open. | Define the typing and state-transition judgments; add positive and negative tests without reopening the adopted decisions. |
| How is continuation typing formalized? | **Decision:** the provider-side continuation is checked against `A`, and the consumer-side continuation against the corresponding consumer-side protocol type, provisionally denoted `dual(A)`. This notation is not an established grammar construct. The formal judgments and channel-identity substitution remain open. | Define the typing judgments and consumer-side protocol type representation; test valid and invalid continuation pairs, including channel-identity substitution. |
| How do the publication's continuation notation and actions map to OrgLang's participant-specific continuations and runtime operations? | The OrgLang endpoint obligations are adopted; the correspondence between the publication's notation/actions and OrgLang's runtime operations remains open. | Verify provider/consumer polarity and action correspondence against language rules and runtime paths; do not infer runtime semantics from publication wording alone. |
| What is the lifecycle of the private physical channel resource after `Down`? | Whether the resource is destroyed, recycled, or retained after the matched `detach`/`release` transition restores the original public channel identity. | Specify resource disposal/reuse separately from the already-decided logical identity, public-state transition, and participant-specific continuation requirements. |
| How do cancellation, failure, and concurrency affect pending or matching `Up`/`Down` interactions? | Whether a pending participant can withdraw, how peer absence or failure is handled, and which interleavings are permitted around a matched transition. | Specify cancellation and failure semantics without weakening the adopted rule that the public protocol transition occurs only when the corresponding operations match; add interleaving and peer-absence tests. |
| Can individual processes expose public transaction channels, or is this pool-only? | Public API and which entity owns the public protocol endpoint. | Project decision grounded in language examples or source rules; inspect implementation only as conformance evidence. |

| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |

### Minimum conformance test matrix

The following is an acceptance target for the adopted semantics, not a description of tests already present. Each pending case should be tested with both endpoint arrival orders, and each matched case should assert the observable post-state rather than only the absence of an API error.

- **Pending boundary:** after only `accept` or `acquire` (and separately only `detach` or `release`), assert that no protocol transition has occurred, no continuation has become eligible, and no participant can observe a partially changed channel state.
- **`Up` match:** after both `accept` and `acquire` match, assert one shared fresh private channel identity, the expected residual protocol state, and exactly one eligibility event for each non-null participant continuation. Use different provider/consumer continuation expressions to ensure they are not accidentally conflated.
- **`Down` match:** after both `detach` and `release` match, assert restoration of the original public channel identity (not a newly allocated public identity), the expected residual protocol state, and exactly one eligibility event for each participant-specific continuation. Include distinct continuation expressions and positive/negative typing cases for each endpoint.
- **`One` match:** assert that a lone `close` or `wait` remains pending; after the pair matches, assert completion with one shared channel identity, no provider-side executable continuation, and eligibility of the consumer's enclosing continuation when present.
- **Representation path:** round-trip every operation and continuation through AST, adapter, persistence, and executor representations. In particular, `Down` cannot pass the language-level continuation tests until both operation specs and their conversion paths can carry the required `ContExp` values.
- **Linearity and isolation:** reject duplicate/aliased channel identities and invalid endpoint continuation types; verify that a pending or matched operation does not mutate unrelated channels or another participant's bindings.

The current inspected `go-engine` paths provide useful pending/matching implementation observations, but the existing end-to-end scenarios include missing result assertions, and the `Down` operation representation does not yet expose the adopted language-level continuation expressions. These are implementation gaps to address, not reasons to weaken the acceptance criteria.
