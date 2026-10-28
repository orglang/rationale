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
| Transaction | A private communication relationship between pools, used to exchange protocol messages. | **Inferred** from the explanatory model. Creation, ownership, cancellation, and completion rules are not fully specified. |
| Transaction identifier | An identifier used to refer to a transaction/channel in the pool model. | **Inferred**. The identifier's concrete representation and allocation/uniqueness guarantees are **Open**. Do not assume it is identical to a process channel identity without evidence. |
| Transaction type | A protocol description governing which transaction messages or transitions are permitted. | **Inferred** from the companion model's transaction-type grammar. Exact OrgLang syntax, checking rules, and runtime enforcement remain **Open**. |
| Pool's public transaction channel | The channel through which a client interacts with the pool-level transaction protocol. | **Inferred** from [issue #85](https://github.com/orglang/go-workspace/issues/85) and the current explanatory model. Whether individual processes can expose analogous public channels remains **Open**. |
| Process provider channel | The channel on which a process incarnation provides its named-process service. | Defined in [Processes and session types, Section 2](../about-processes-and-session-types/README.md#2-core-concepts). It is distinct from the pool's public transaction channel. |

A transaction identifier and a process channel identity must not be conflated merely because both are called identifiers or channels. The current model uses identifiers for different resources depending on interpretation; a precise mapping requires evidence from the language contract or a verified execution path.

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
| How are pool eligibility and process-name matching determined from the pool's transaction-type agreement? | **Open** | Determines how a candidate pool's established agreement is related to the named process and when that agreement counts as suitable. | A precise matching rule and positive/negative examples; do not assume a separate compatibility mechanism beyond the agreement itself. |
| Are constraints on pool state part of type checking, runtime validation, or both? | **Open** | Determines which constraints expressed by the transaction-type agreement are checked statically and which require runtime validation. | A typing/validation rule and implementation-path evidence, with negative examples. |
| How do dependent types express agreement-specific details, and how do those details participate in matching or instantiation? | **Open** | Determines how participant-specific or agreement-specific terms are expressed within the transaction-type agreement. | A project decision about dependent-type meaning and its role in matching/instantiation; the transaction type itself is the agreement, not a separate mechanism. |

The detailed eligibility question and the evidence needed to resolve it are tracked in the table above; the search procedure itself remains canonical in [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing).

**Working project direction (partly open):** the transaction type is the agreement between the client and the pool; it is not a separate mechanism from that agreement. Dependent types may express details specific to a particular agreement, but the exact meaning of those details and their role in matching versus agreement-specific instantiation remain open. **Agreed project decisions:** automatic search looks among previously established agreements. If it finds no suitable agreement, manual intervention always follows; a participant of the calling pool can select a candidate pool to begin negotiating a new agreement. A pool may participate in multiple previously established agreements. If automatic search finds multiple suitable agreements, a selection order exists, but its rules remain open. **Agreed project decision:** the agreement-search timeout belongs to the search mechanism, not to the transaction type. Expiry therefore indicates that this search has terminated under its time limit; it does not by itself establish that the candidate types are incompatible or that no suitable agreement exists. The timeout's operational boundary is specified in [Process creation and pool selection, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). The calling pool supplies one shared timeout setting for all agreement searches initiated by calls from that pool. Its configuration interface, representation, and valid range remain open.

## 5. The pool's public transaction channel

**Inferred:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public transaction channel. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Inferred working model; return-to-public-channel behavior is a project decision:** access through the pool's public transaction channel gives the client a private channel for the duration of the critical section. Exclusivity applies to this private channel and its interaction; separate client interactions fall outside that scope. Reaching `Down` ends this private interaction: after provider-side `detach` and client-side `release` match, the client loses the private channel and returns to the pool's public transaction channel. The public channel is the pool-level entry point; it is not the private channel that was used inside the critical section.

What happens next depends on `ContExp`, the continuation expression associated with the `Down` transition. Returning to the public channel does not, by itself, guarantee that another `Up` can happen immediately, nor does it imply that the pool must perform an additional action first. The continuation determines the next interaction permitted by the protocol.

Each interaction generates a new channel identity for its continuation, reflected in the channel's type. The private channel's resource disposition beyond the client's loss of access to it—such as whether the underlying resource is destroyed or recycled—remains unspecified. The return-to-public-channel rule does not by itself imply resource destruction, pool-state changes, or process termination.

This pool-level protocol is conceptually distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Process creation and pool selection](../about-spawn/README.md).

## 6. Intended semantics and formal rules

This section records the agreed minimal language-level decisions for matching and continuation behavior, while leaving a complete operational semantics unfinished. The decisions below specify when the protocol transition counts as occurring; they do not establish implementation correctness, complete typing rules, failure semantics, or every state transition.

### 6.1 Minimal transaction-type constructors

**Status: Inferred working semantics**, grounded in the project's current mapping between transaction-type constructors and the provider/client operations represented in `orglang/go-engine`. This subsection records the proposed minimum contract; it is not yet a normative operational semantics.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A client's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared client-side transaction type is required by this model.

| Constructor | Provider-side operation | Client-side operation | Minimal intended meaning | Boundary and limitation |
|---|---|---|---|---|
| `One` | `close` | `wait` | The provider performs the terminal `close` interaction; the client waits for that interaction. After a successful `wait`, the client's enclosing expression may continue according to its surrounding expression. | **Decision:** the transaction completes only when the operations match, and matching establishes one new channel identity shared by both sides. This shared identity does not imply that both operations carry executable continuation expressions: in the current model, the client's `wait` may have an enclosing continuation, while provider-side `close` is terminal for this protocol interaction. `One` does not itself imply process termination. Continuation scheduling and failure behavior remain open. |
| `Up A` | `accept` | `acquire` | The provider accepts the access interaction and the client acquires access. The provider-side continuation is checked against `A`; the client-side continuation is checked against the corresponding client-side protocol type (provisionally denoted `dual(A)` in this document, not an established grammar construct). | **Decision:** access starts only when the operations match; both continuations use one new shared channel identity. The complete typing judgment, implementation linearization, and failure behavior remain open. |
| `Down A` | `detach` | `release` | The provider detaches or withdraws the current access; the client releases that access. The provider-side continuation is checked against `A`; the client-side continuation is checked against the corresponding client-side protocol type (provisionally denoted `dual(A)` in this document, not an established grammar construct). | **Decision:** access ends only when the operations match, and matching establishes one new channel identity shared by both sides. In the intended operation model, both `detach` and `release` carry participant-specific continuation expressions (`ContExp`); these need not be identical but must satisfy their respective endpoint typing obligations. The complete typing judgment remains open. Resource disposition and process termination are not implied. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/client operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

#### Continuation correspondence: dual endpoint views

**Decision recorded from semantic review:** `A` describes the provider-side continuation protocol; the client-side continuation must be checked against the corresponding client-side protocol type. For brevity, this document uses `dual(A)` as a provisional notation for that client-side type. This notation is introduced here for explanatory purposes only: it is not an established OrgLang grammar constructor or operation, and no definition or derivation rule for it is assumed. The participant-specific continuation expressions need not be textually identical, but each must satisfy the typing obligation for its own endpoint. Matching the operation pair and binding one shared new channel identity do not, by themselves, make arbitrary `ContExp` values valid.

This decision establishes the intended endpoint relationship, not the complete typing judgment. The formal representation of the client-side type, the typing rules, and how the continuation channel identity is substituted into each participant's continuation remain to be specified and tested.

#### Transition obligations to settle

Before treating the table as normative, specify for each paired operation:

- **Precondition:** the current protocol state, participant roles, and any agreement/access prerequisites.
- **Action and matching:** which operation enables or matches the peer operation, and whether matching is atomic or has observable intermediate states.
- **Result:** the next protocol state and the continuation/channel identity available to each participant.
- **Failure boundary:** what happens when the peer operation is absent or the protocol state does not permit the operation. Error recovery and retries remain outside this initial proposal unless they affect safety.
- **Evidence:** the language-level rule, then implementation-path and observable-test evidence for conformance.

#### Initial conformance examples

These are acceptance criteria for future tests, not claims that tests already exist or pass:

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

Until these points are settled, keep the rule explicitly **Inferred** or **Open** and link to the relevant question in Section 9.

## 7. Publication correspondence

The [transaction introduction](../about-transaction/README.md) contains a formal model and a transaction-type table. Its Table 4 says that `↑ A` sends a `grant` token and continues as `A`, while `↓ A` accepts a `revoke` token and continues as `A`. The continuation grammar and application rules (Tables 2 and the definition of `V ▷ K`) explain how a received value selects a continuation and substitutes an identifier for a placeholder.

This establishes that the publication model associates `↑ A` and `↓ A` with continuation behavior at the type level. It does **not** establish that OrgLang's provider-side and client-side operation expressions must be identical, that both runtime operations carry `ContExp`, or how one type-level `A` constrains two participant-specific continuations. Those are separate correspondence/typing questions. The publication table's send/accept wording also should not be equated mechanically with the current runtime operation names (`accept`/`acquire`, `detach`/`release`) without an explicit role and polarity mapping.

### Initial constructor/role correspondence table

The table below separates the publication model's token polarity from OrgLang's current provider/client operation names. It is a working correspondence, not a claim that the runtime implementation already conforms.

| Type constructor | Publication-level action | Provider-side OrgLang operation | Client-side OrgLang operation | Established minimum | Still open |
|---|---|---|---|---|---|
| `One` (`𝟏`) | The provider-side type sends `close`; the client-side dual action receives/waits for it. | `close` | `wait` | The pair must match before the interaction counts as complete; matching establishes one shared new channel identity. | Whether the publication's terminal `close` case directly corresponds to the client's enclosing continuation, and how the shared identity is typed for this terminal case. |
| `Up A` (`↑ A`) | The provider-side type sends `grant`, then continues as `A`; the client performs the complementary receive/acquire action. | `accept` | `acquire` | Access starts only when the pair matches; both participants use the shared new channel identity. | The exact operational meaning of `accept` versus `acquire`, and the precise typing obligation on each participant continuation. |
| `Down A` (`↓ A`) | The provider-side type accepts/receives `revoke`, then continues as `A`; the client performs the complementary send/release action. | `detach` | `release` | Access ends only when the pair matches; both participant-specific `ContExp` values are enabled after matching and use the shared new channel identity. | The exact operational meaning of `detach` versus `release`, how the two participant continuations are constrained by `A`, and how the type-level continuation identity relates to runtime channel identity. |

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
| [`pool/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/compexec/core/core.go), `take` cases for `DetachSpec` and `ReleaseSpec` | The same pending-subscription pattern is used. On matching, the implementation creates a new channel ID and binds both continuation channels; these operations do not schedule a continuation expression in the inspected cases. | The current implementation models `detach`/`release` as a paired interaction with a continuation channel after matching. | Resource disposition after the interaction and any broader lifecycle contract. |
| [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/core/core.go) and [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go), operation-spec declarations | In both packages, `DetachSpec` and `ReleaseSpec` contain only `CommChnlPH`; neither declares a `ContExp` field. By contrast, `AcceptSpec` and `AcquireSpec` declare `ContExp`. In the process package, `CloseSpec` has no `ContExp`, while `WaitSpec` does. | The inspected runtime data structures do not directly represent the agreed participant-specific continuation expressions for `Down` on `detach` and `release`; `Up` has continuation fields on both operations. | Whether continuation behavior is represented elsewhere or whether the operation model/type checker/executor must change. This source inspection alone does not establish system-wide absence or authorize implementation changes. |
| [`proc/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/compexec/core/core.go), `takeWith` cases for `CloseSpec` and `WaitSpec` | If no opposite operation is registered, the executor records a pending subscription and returns. On matching `close`/`wait`, it creates a new channel ID and binds both sides to the `One` continuation type; the wait-side continuation is scheduled when non-nil. | The inspected process executor uses the same pending-then-match pattern for `One`. | Whether the language contract requires this exact scheduling/observability behavior, and abnormal termination/error behavior. |
| [`pool/termexp/adapter/tc.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/pool/termexp/adapter/tc.go) | The adapter maps the core operation specifications to SDK operation variants with corresponding names. | The operation names are carried through the adapter. | An adapter mapping alone does not establish protocol correctness or type conformance. |
| [`test/e2e/pool_test.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/test/e2e/pool_test.go), `TestPool` / `waitClose` | The test builds an `Up`/`With`/`Down` pool type and exercises some pool acquisition/acceptance steps. The `close`/`wait` process interaction and final outcome assertion are commented out; the test contains a TODO for an assertion. | This file provides an example of intended test setup and partial execution coverage. | It does not currently establish an asserted end-to-end `One` outcome or full conformance for `Up`/`Down`. The test was inspected, not run in this task. |

These paths suggest that the implementation has a **pending registration** stage followed by a **matching/continuation-binding** stage. Do not call the whole interaction atomic without defining the relevant observable boundary: the database mutation and broker scheduling path, and concurrent interleavings, would need to be traced to settle that question.

### 8.1 Proposed language-level rule: access begins on matching

**Decision recorded from semantic review:** for `Up`, access becomes active only when the provider-side `accept` and client-side `acquire` have been matched. Issuing either operation alone is not sufficient to establish access. A pending operation is a waiting state, not an active-access state.

At the matching point, the semantics must establish the continuation channel for both participants and permit their continuations to proceed according to the protocol. The exact linearization/observability boundary, including failure and cancellation between registration and matching, remains to be specified; this decision does not assert that the current implementation has already been verified against every interleaving.

**Decision recorded from semantic review — `Down`:** access ends only when provider-side `detach` and client-side `release` have been matched. Registering either operation alone leaves the protocol's access state unchanged: access remains active until the pair matches. The pending registration does not itself change the publicly observable protocol state, and neither side may treat access as fully ended before the match. Both participant continuations are enabled only after the match; the exact implementation observable boundary and behavior under cancellation or failure before matching remain open.

**Decision recorded from semantic review — `One`:** the transaction is complete only when provider-side `close` and client-side `wait` have been matched. Registering either operation alone does not complete the transaction; a pending operation remains unresolved until its peer operation matches. The exact observable transition boundary, and behavior under cancellation or failure before matching, remain open.

### 8.2 Matching boundary and continuation behavior

**Decisions recorded from semantic review:**

- For each of the three operation pairs in Section 8.1, registering only one side creates a pending operation; it does not itself change the transaction's publicly observable protocol state. The language-level transition occurs when the two corresponding operations match.
- After matching, participants may proceed through any continuations provided by their respective operations, independently and subject to the transaction type. For `Up` and the intended `Down` model, this means participant-specific continuations on both sides. For `One`, the client's `wait` may continue in its enclosing expression, while provider-side `close` is terminal; the shared channel identity does not imply a provider-side executable continuation. Matching imposes no additional ordering between continuations that exist and does not guarantee simultaneous execution.
- For each of `One`, `Up`, and `Down`, matching establishes one new channel identity shared by both sides; the rule is not to allocate two independent identities. For `Up`, both participants' continuations use that shared identity. For `One`, identity sharing is a channel-binding rule, not a claim that both sides have executable continuation expressions.
- For `Down A`, both `detach` and `release` are intended to carry participant-specific continuation expressions (`ContExp`), which need not be identical. Neither continuation is executed before the pair matches. After matching, each participant may proceed through its own continuation; `A` describes the protocol continuation associated with the shared new channel identity, not a requirement that both participants execute the same expression. Matching imposes no additional ordering between the continuations and does not guarantee simultaneous execution.

These are language-level semantic decisions, not a claim that every implementation interleaving has been verified. The exact implementation linearization point, cancellation/failure behavior, and other abnormal interleavings remain out of scope for this pass. Cancellation semantics are explicitly deferred.

This is a language-level design decision; it does not claim that the current `go-engine` operation specs already expose these continuation fields. The next implementation work, if authorized, should align the AST/operation model, typing, adapters, executor, and tests with this decision. Absence from the paths above does not establish system-wide absence.

## 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| Which transaction-type constructors and syntax are part of OrgLang, rather than only the companion model? | Grammar, type checking, and compatibility of programs. | Adopted grammar/project decision; compare parser and type-checker support separately. |
| What remains to be specified about `One`, `Up`, and `Down` transitions? | Matching points and the shared-new-identity rule for all three constructors are decided; the relationship between type continuations and participant-specific operation continuations, type-state progression, ownership, and observable boundaries remain open. | Specify the relationship between the resulting channel's protocol type and each participant's continuation expression; then add tests for permitted and prohibited transitions without reopening settled matching or shared-identity decisions. |
| What makes a participant continuation valid for `A`? | **Decision:** the provider-side continuation is checked against `A`, and the client-side continuation against the corresponding client-side protocol type, provisionally denoted `dual(A)` in this document. `dual(A)` is not an established grammar construct. The formal representation and channel-identity substitution remain Open. | Define the typing judgments and formal representation of the client-side protocol type; test valid and invalid continuation pairs, including continuation-channel substitution. |
| What does the publication model establish about `Up A` / `Down A` continuation typing? | The publication describes continuation `A` at the provider-side type; the adopted OrgLang design checks the provider continuation against `A` and the client continuation against the corresponding client-side protocol type, provisionally written `dual(A)`. This notation is explanatory shorthand, not a language construct. The exact mapping from publication actions to runtime operations remains Open. | Define the typing judgments and the formal representation of the client-side protocol type; keep `dual(A)` as convenient notation unless a language-level construct is explicitly adopted. Verify the provider/client polarity mapping against language rules and runtime operation paths. |
| What happens after `Down`? | **Decision:** after `detach`/`release` match, the client loses the private channel and returns to the pool's public transaction channel. The next permitted behavior depends on `ContExp`; immediate reuse is not implied. The underlying private resource's destruction or reuse remains open. | Specify the continuation rules for `ContExp`; test that the private channel is no longer usable by the client after `Down`, that the public pool channel is returned, and separately specify resource disposal/reuse. |
| Are `accept`/`acquire` and `detach`/`release` atomic paired transitions, or can intermediate states be observed? | Ordering, concurrency, cancellation, and whether access can be considered active before both participants have matched. | Specify transition boundaries and observable state; add tests for interleavings and peer absence. |
| Can individual processes expose public transaction channels, or is this pool-only? | Public API and which entity owns the public protocol endpoint. | Project decision grounded in language examples or source rules; inspect implementation only as conformance evidence. |
| How does an established transaction-type agreement qualify a pool to service a named process? | Whether the agreement's association with the process name is sufficient for selection, and which agreement-specific details may also matter. | Align the selection rule with [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing); add positive and negative examples without assuming a separate compatibility mechanism. |
| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |
