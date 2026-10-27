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
| What are the exact transition rules for `One`, `Up`, and `Down`, including matching, ordering, and continuation/channel identity? | **Open** | Determines when an operation is enabled, when each participant may continue, and what state is observable between peer operations. | Adopt the obligations in Section 6.1 as explicit rules; then test both permitted and prohibited transitions. |
| How are pool eligibility and process-name matching represented in a transaction type? | **Open** | Determines whether a candidate pool is eligible and whether matching is static, dynamic, or both. | An explicit agreement/type contract and examples distinguishing eligible from ineligible pools. |
| Are constraints on pool state part of type checking, runtime validation, or both? | **Open** | Determines which constraints are checked statically and which require runtime validation. | A typing rule and implementation-path evidence, with negative examples. |
| How exactly does a transaction type represent a pool agreement, including dependent details specific to a particular agreement? | **Open** | Determines how agreement terms, participant-specific details, and compatibility are represented. | A project decision specifying the agreement/type relationship and how dependent types participate in it; do not infer a checking or instantiation algorithm yet. |

The detailed eligibility question and the evidence needed to resolve it are tracked in the table above; the search procedure itself remains canonical in [Process creation and pool selection, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing).

**Working project direction (partly open):** a pool agreement is understood as a transaction type, and dependent types provide a mechanism for expressing details specific to a particular agreement. The precise relationship between a type, the participants, and a concrete agreement is not yet settled; neither is the role of dependent types in candidate matching versus agreement-specific instantiation. **Agreed project decisions:** automatic search looks among previously established agreements. If it finds no suitable agreement, manual intervention always follows; a participant of the calling pool can select a candidate pool to begin negotiating a new agreement. A pool may participate in multiple previously established agreements. If automatic search finds multiple suitable agreements, a selection order exists, but its rules remain open. **Agreed project decision:** the agreement-search timeout belongs to the search mechanism, not to the transaction type. Expiry therefore indicates that this search has terminated under its time limit; it does not by itself establish that the candidate types are incompatible or that no suitable agreement exists. The timeout's operational boundary is specified in [Process creation and pool selection, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). The calling pool supplies one shared timeout setting for all agreement searches initiated by calls from that pool. Its configuration interface, representation, and valid range remain open.

## 5. The pool's public transaction channel

**Inferred:** the public channel discussed in [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85) is the pool's public transaction channel. Whether individual processes should have public channels remains **Open**.

The pool's public transaction channel has a transaction type of the form `Up` followed by a continuation that ultimately ends in `Down`.

**Inferred:** access through the pool's public transaction channel gives the client a private channel for the duration of the critical section. Exclusivity applies to this private channel and its interaction; separate client interactions fall outside that scope. Reaching `Down` marks the end of this protocol-bounded critical section; the client interaction along that channel continuation ends there.

Each interaction generates a new channel identifier for its continuation, reflected in the channel's type. Resource lifecycle after `Down`—closure, return to the pool, or another disposition—remains unspecified pending a precise account of the `Up` / continuation / `Down` semantics.

This pool-level protocol is conceptually distinct from a process's provider channel and from channels mapped to a new incarnation's client-role parameters in `ExternalCall`. Process creation, pool selection, and the start of servicing are described in [Process creation and pool selection](../about-spawn/README.md).

## 6. Intended semantics and formal rules

This section does not yet define a complete operational semantics. The current working claims in Section 5 are **Inferred**; they should not be promoted to language rules until their preconditions and transitions are agreed and supported.

### 6.1 Minimal transaction-type constructors

**Status: Inferred working semantics**, grounded in the project's current mapping between transaction-type constructors and the provider/client operations represented in `orglang/go-engine`. This subsection records the proposed minimum contract; it is not yet a normative operational semantics.

A transaction type describes the protocol exposed by a pool through its public transaction channel. A client's interactions must conform to this provider-side protocol, evaluated against the current protocol state. No separately declared client-side transaction type is required by this model.

| Constructor | Provider-side operation | Client-side operation | Minimal intended meaning | Boundary and limitation |
|---|---|---|---|---|
| `One` | `close` | `wait` | The provider performs the terminal `close` interaction; the client waits for that interaction. After a successful `wait`, the client's enclosing expression may continue according to its continuation. | `One` is terminal for this protocol interaction. It does not, by itself, imply termination of the client process. Exact matching and scheduling rules remain open. |
| `Up A` | `accept` | `acquire` | The provider accepts the access interaction and the client acquires access; both sides have continuations corresponding to `A`. | The exact pairing point, channel identity/ownership, and whether the two operations form one atomic transition remain open. |
| `Down` | `detach` | `release` | The provider detaches or withdraws the current access; the client releases that access. | This ends the current access interaction. It does not specify what happens to the underlying resource afterward, nor does it imply termination of either process. Neither operation has a continuation in the current operation model. |

The operation names above are implementation identifiers, not proposed surface syntax. The pool-side operation declarations are in [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go); the process-side declarations are in [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/8ef6983f7a112616ee3f78d4f98e615686931e6a/proc/termexp/core/core.go). These declarations support the provider/client operation mapping, but by themselves do not establish the runtime transition order or full language semantics.

#### Transition obligations to settle

Before treating the table as normative, specify for each paired operation:

- **Precondition:** the current protocol state, participant roles, and any agreement/access prerequisites.
- **Action and matching:** which operation enables or matches the peer operation, and whether matching is atomic or has observable intermediate states.
- **Result:** the next protocol state and the continuation/channel identity available to each participant.
- **Failure boundary:** what happens when the peer operation is absent or the protocol state does not permit the operation. Error recovery and retries remain outside this initial proposal unless they affect safety.
- **Evidence:** the language-level rule, then implementation-path and observable-test evidence for conformance.

#### Initial conformance examples

These are acceptance criteria for future tests, not claims that tests already exist or pass:

1. **`One`:** a client waiting for the provider's `close` may proceed to its own continuation only after the close interaction is observed; the close interaction does not itself terminate the enclosing client process.
2. **`Up`:** a client cannot treat access as acquired unless the provider-side protocol permits and matches the acquisition; both participants continue according to the continuation associated with `Up`.
3. **`Down`:** after a valid detach/release interaction, the current access cannot be treated as still active. The test must not assume resource destruction, reuse, or process termination unless a separate lifecycle rule specifies it.
4. **Protocol conformance:** an operation that contradicts the current provider-side protocol state is rejected or otherwise prevented according to a separately specified checking/enforcement rule; that enforcement mechanism is currently open.

For each rule adopted in this section, record:

1. **Preconditions:** the participant roles, channel/type state, and any agreement or resource prerequisites.
2. **Action:** which participant sends, receives, selects, or applies a continuation.
3. **Result:** the next protocol state, the identity and ownership of any channel/resource, and any change to pool state.
4. **Observable state at a transition boundary:** where relevant, state the pre-state/post-state and ordering constraints needed to preserve protocol and resource invariants. Detailed error reporting, recovery, retries, and abnormal-termination semantics are outside this specification pass.
5. **Evidence:** the source for the intended language rule, plus separate implementation-path/test evidence where conformance is claimed.

Until these points are settled, keep the rule explicitly **Inferred** or **Open** and link to the relevant question in Section 9.

## 7. Publication correspondence

The [transaction introduction](../about-transaction/README.md) contains a formal model and a transaction-type table. This section's future comparison must identify the exact rule/table entry in that model and state only what it establishes about the model presented there. Correspondence to OrgLang is a separate claim.

The initial comparison should cover:
- the grammar and reduction/application operation for values, continuations, and pool terms;
- the transaction-type constructors and their side conditions;
- the relationship between a type's constraints and the pool-state set used by the model;
- the spawn-form rule and its relationship, if any, to OrgLang's `SpawnSpec`.

**Open:** whether these publication constructs correspond one-to-one to OrgLang constructs. Similar names or matching notation are not sufficient evidence.

## 8. Implementation evidence

Implementation conformance has not been established by this document. Before making a concrete claim, trace the relevant parser/AST, type checker, adapter, and execution path, and cite the exact files/symbols or tests inspected.

The first evidence pass should answer:
- Where are transaction-type constructors represented and validated?
- Is the pool public channel's `Up … Down` protocol represented in types, runtime state, or both?
- Where is a transaction identifier allocated, checked for uniqueness, and associated with a continuation?
- What execution path handles pool messages and the spawn-form construct?
- Which tests assert observable outcomes, rather than merely executing a path?

Record each finding as an implementation observation with coverage status; absence from one inspected path does not establish system-wide absence.

## 9. Open questions and next tests

| Open question | Behavior/decision affected | Evidence or test needed |
|---|---|---|
| Which transaction-type constructors and syntax are part of OrgLang, rather than only the companion model? | Grammar, type checking, and compatibility of programs. | Adopted grammar/project decision; compare parser and type-checker support separately. |
| What do `Up`, its continuation, and `Down` guarantee? | Direction of communication, continuation obligations, and end of the protocol-bounded critical section. | Explicit transition rule plus tests for valid and invalid continuation sequences. |
| What happens to the private channel and associated resources after `Down`? | Resource ownership, reuse, closure, and potential leaks or aliasing. | Explicit lifecycle decision; tests for subsequent use and resource disposition. |
| Are `accept`/`acquire` and `detach`/`release` atomic paired transitions, or can intermediate states be observed? | Ordering, concurrency, cancellation, and whether access can be considered active before both participants have matched. | Specify transition boundaries and observable state; add tests for interleavings and peer absence. |
| Can individual processes expose public transaction channels, or is this pool-only? | Public API and which entity owns the public protocol endpoint. | Project decision grounded in language examples or source rules; inspect implementation only as conformance evidence. |
| How is pool eligibility encoded and checked? | Selection outcome and whether an apparently matching pool may still reject service. | Agreement/type rule plus positive and negative examples; identify static/runtime validation boundaries. |
| How are agreement parameters and timeout values represented? | Who supplies timeout, how it is checked, and whether it is static or dynamic. | Project decision; do not assume the proposed `0 = infinite` convention. |
| How are transaction identifiers allocated and related to process channel identities? | Identity uniqueness, resource ownership, and safe continuation substitution. | Identity contract and source/test evidence for allocation and substitution. |
| Which implementation paths establish conformance? | Confidence that intended protocol rules are executable. | Source-level trace and tests with observable assertions for each agreed rule. |
