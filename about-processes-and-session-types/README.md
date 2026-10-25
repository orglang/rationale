# Processes and session types

> **Status: preliminary research draft.** This document separates intended OrgLang semantics from observations about `orglang/go-engine`. Formal rules should describe language behavior independently of Go structure and field names. Implementation notes track evidence, discrepancies, and questions requiring verification. AST syntax alone does not establish complete runtime semantics for an expression.

**Audience:** readers who need to understand OrgLang process expressions and session types, and contributors verifying how those concepts are represented in `orglang/go-engine`. This research draft records the current model and evidence pending a normative language specification.

**How to use this document:**
- Parts I and II describe the language model, intended operation semantics, and comparison with the publication.
- Part III records implementation evidence and open questions. The intended language semantics are stated in Part I.
- Section 1 explains the three independent status dimensions. Section 14 collects the remaining verification questions.

**Contents**
- [Part I — Language model](#part-i-language-model): [core concepts and glossary](#2-core-concepts), [protocol example](#3-a-small-example-following-a-channel), [session types](#6-session-types-the-protocol-for-a-channel), and [intended operation semantics](#7-intended-semantics-of-named-process-calls).
- [Part II — Comparison with the publication](#part-ii-comparison-with-the-publication): publication rules and forwarding trace.
- [Part III — Implementation evidence and open questions](#part-iii-implementation-evidence-and-open-questions): [implementation map](#9-implementation-map-process-declarations-and-definitions), [typing](#10-typing-interface), [execution](#11-execution-and-communication), [AST and serialization gaps](#12-ast-and-serialization-gaps), and [open questions](#14-open-questions-and-next-tests).

## Part I. Language model

## 1. Scope and evidence

This research draft describes OrgLang processes and session types, compares the intended model with the supplied publication, and records implementation evidence from `orglang/go-engine`. Pool and transaction semantics are covered separately, with pool-level process creation included where it clarifies the boundary between invocation and spawning.

Treat each source according to what it can establish: the publication supports claims about its own rules, while implementation code supports claims about the inspected implementation. Neither automatically establishes a normative OrgLang rule.

Three status dimensions must remain separate:

| Dimension | Values | Question it answers |
|---|---|---|
| Claim evidence | **Confirmed**, **Inferred**, **Open** | What does the available evidence establish about this claim? |
| Implementation coverage | **Implemented**, **Partial**, **Absent**, **Unverified** | How much of the relevant behavior has been verified in the implementation? |
| Terminology mapping | **Confirmed**, **Provisional**, **Unresolved** | How strong is the proposed correspondence between OrgLang, publication, and implementation terms? |

For example, a project decision can confirm the intended direction of OrgLang behavior while implementation coverage remains unverified. Identify the decision as the source and state what it explicitly establishes. A claim about a formal language rule needs support from a normative specification or an explicitly adopted language-level contract.

### Evidence status

Assign status to each individual claim. A term may appear in claims with different evidence statuses.

- **Confirmed** — the claim is directly supported by an appropriate source or by sufficient verified evidence. State what the evidence establishes.
- **Inferred** — the claim is a working interpretation derived from available evidence, but is not directly established.
- **Open** — available evidence does not settle the claim, or relevant verification has not been completed.

Use the source to distinguish a language rule, a publication rule, and an implementation observation. A claim confirmed by one source is not automatically confirmed for another. An implementation observation alone establishes neither a language rule nor a language-level prohibition; an unstated guarantee leaves the opposite behavior unspecified.


### Implementation status

Track implementation coverage independently from evidence status.

- **Implemented** — the relevant behavior has been verified in the execution path or by an appropriate test.
- **Partial** — some of the required behavior is implemented, but coverage is incomplete.
- **Absent** — inspection or testing establishes that the relevant behavior is not implemented in the scope examined.
- **Unverified** — implementation coverage has not been established.

An AST constructor establishes syntax support. Runtime support requires evidence from the relevant execution path or tests; inspection of one code path alone cannot establish system-wide absence.

### Recording claims

For substantial or disputed claims, record the claim, source, evidence status, implementation status (when relevant), and any limitation or next verification step. Keep glossary entries lightweight; use the full record for semantic rules, implementation claims, and cross-source discrepancies.

Distinguish three kinds of statement in prose:

- **Language rule** — a rule established for OrgLang.
- **Implementation observation** — behavior or structure found in the inspected implementation.
- **Candidate rule** — a proposed interpretation awaiting verification or a design decision.

Do not promote a candidate rule to a language rule merely because it is described in detail or reflected in the current code. Record unresolved questions and the evidence needed to resolve them.

### Terminology mappings

The terminology table tracks correspondence among OrgLang, publication, and implementation identifiers. Mapping status reports correspondence strength; claim evidence and implementation coverage are tracked separately.

Use **Confirmed**, **Provisional**, or **Unresolved** for mappings:

- **Confirmed** — the correspondence is supported by sufficient evidence.
- **Provisional** — evidence supports the correspondence, but it still needs verification.
- **Unresolved** — no correspondence is established, or sources appear to conflict. Describe any discrepancy in the mapping table's **Notes** column.

Record mismatches explicitly; treat similarly named concepts as equivalent only when evidence supports that mapping.

## 2. Core concepts

OrgLang processes communicate through **channels**. A channel connects two roles: the **provider**, which offers a service, and the **client**, which uses it. Each participant has an **endpoint**; the same channel is the provider channel for one process and the client channel for the other. These roles are relative to each process's perspective. Each process has one provider channel of its own and may use other channels as a client. The two named-process call forms are **`ExternalCall`** and **`InternalCall`**. Both create a fresh process incarnation, but transfer channels in different directions relative to that incarnation.

**Process** is the general umbrella term in this document; its precise referent follows context. A **named process** is the process identified by a name. A **process declaration** describes its interface, while a **process definition** supplies its behavior. Each start creates a concrete running copy called a **process incarnation**. Every process incarnation receives an identity that is never reused: once an identity has been allocated, no later incarnation may receive it, even after the original incarnation terminates. This is a model-wide identity policy, not an `InternalCall`-specific condition. Each term refers to a distinct concept. A **channel placeholder** is a syntactic name in an expression or process interface that stands for a channel. An environment or substitution associates the name with the relevant channel resource or endpoint. The implementation may represent these layers with different Go types, and the mapping must be verified rather than inferred from field names alone.

A **session type** describes the allowed protocol from the provider endpoint's point of view. When checking the client endpoint, the type checker accounts for the client role and the complementary actions it permits. A **residual session type** is the remaining part of that protocol after prior interaction steps. The request/response example and the meaning of a **residual session type** are introduced in Section 3.

**Linearity** is the channel usage/ownership discipline. **Model invariant:** channel bindings are non-aliasing: distinct bound channel placeholders refer to distinct channel identities. Consequently, distinct formal channel parameters supplied to a call must map to distinct existing channel identities. The no-alias property is a global assumption of the OrgLang model, not a special precondition introduced by `InternalCall`. A call's list of supplied identities covering the set of identities in an environment does not, by itself, establish completeness of the transfer; the environment's full set of bindings must still be accounted for. More generally, **normal completion** of a process is permitted only when its channel protocols permit completion and all linear obligations have been discharged; the inspected type checker rejects a normal-completion attempt while a provider-channel protocol remains unfinished; this is an implementation observation, not yet a complete formal language rule. This is distinct from `InternalCall`, whose agreed semantics terminate the old incarnation by transferring its complete channel environment to a replacement incarnation. That transition is not evidence that the transferred protocols are finished. The full linearity invariant and its application across constructs remain open; do not infer them solely from `InternalCall`.

### Quick glossary

| Term | Meaning in this document |
|---|---|
| Channel | The shared communication resource used by a provider and a client. |
| Endpoint | One participant's role-specific side of a channel: the provider endpoint or the client endpoint. |
| Provider endpoint | The side of a channel belonging to the process that provides the service. |
| Client endpoint | The side of a channel belonging to the process that uses the service. |
| Provider channel | A channel viewed from the process that provides on it; its endpoint in that process is the provider endpoint. |
| Client channel | A channel viewed from the process that uses it; its endpoint in that process is the client endpoint. |
| Provider / client | Roles on the same channel: offering a service / using it. |
| Process | General umbrella term; use context to identify whether it refers to a named process or a running incarnation. |
| Named process | A process referred to by name. |
| Process declaration | The process interface, including its provider-role and client-role channel placeholders. |
| Process definition | The body or expression specifying process behavior. |
| Process incarnation | One running instance of a process. |
| Channel placeholder | A syntactic name intended to be associated with a channel; not the channel resource itself. |
| Session type | The allowed channel protocol, described from the provider endpoint's point of view; type checking accounts for the client role. |
| Residual session type | The part of that protocol still to be performed at the current point. |
| Linearity | Channel usage/ownership discipline. The model disallows aliasing between distinct channel bindings; distinct formal parameters supplied to a call therefore map to distinct existing channel identities. Process completion requires all linear obligations to be discharged. |
| Polarity | An implementation-level positive/negative/neutral classification used by the type checker; operational consequences are documented separately. |
| Snapshot | An implementation concept that may relate to the publication's `configuration` and `environment`; the exact mapping remains open. |
| Turn | The implementation uses turn-like records for pending communication/exchange state; their language-level status and precise semantics remain open. |

### Terminology correspondence: OrgLang, publication, and implementation

Use one row for each proposed correspondence. **Mapping status** reports correspondence strength. Claim evidence and implementation coverage have separate statuses. Apply the mapping-status definitions in [Section 1](#1-scope-and-evidence).

| OrgLang term / concept | Publication term / notation | Implementation name | Mapping status | Notes |
|---|---|---|---|---|
| Provider channel placeholder | Provider-role channel parameter in the process interface | `LiabVar` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| Client channel placeholders | Client-role channel parameters in the process interface | `AssetVars` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| `InternalCall` provider channel (`X`) | No equivalent established in the inspected excerpt | `LinkSpec.X` (AST spelling: process-expression constructor `LinkSpec`) | Unresolved | Intended to denote the existing provider channel, but the field is typed as `identity.ADT`, not a channel-placeholder symbol. Runtime resolution is unverified. |
| `InternalCall` client channels (`Ys`) | No equivalent established in the inspected excerpt | `LinkSpec.Ys` (AST constructor: `LinkSpec`) | Unresolved | Intended to denote client channels in declaration order; representation and runtime resolution are unverified. |
| `ExternalCall` | `a ← p b`; publication substitution rule | `CallSpec`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, `NewChnlPH` | Provisional | Publication supports invocation and substitution; see Section 7 for the intended contract and Section 14 for unresolved details. Implementation mapping remains unverified. |
| `InternalCall` | No equivalent established | `LinkSpec` (implementation AST spelling `Link`) | Unresolved | Agreed intended behavior transfers all channels bound to the invoking incarnation into a fresh incarnation and semantically terminates the old incarnation; no complete adapter/executor path was found. |
| Send/publish action (`pub`) | `msg` | `PubRec`, `ValExp` | Provisional | The names align with the send/message side in the described forwarding trace; end-to-end state semantics remain open. |
| Service/wait action (`sub`) | `srv` | `SubRec`, `ContExp` | Provisional | The names align with the service/waiting side in the described forwarding trace; end-to-end state semantics remain open. |
| Residual session type | Remaining protocol after an interaction step | Current session-type value / checker context (`LinearVars`) | Unresolved | Conceptual correspondence only; state-update invariants remain open. |
Record mismatches among OrgLang terminology, publication terminology, and implementation names. Treat these terms as synonyms only when evidence supports the mapping. Intended behavior is described in Section 7; implementation findings and remaining questions are separated in Part III.




## 3. A small example: following a channel

Imagine two processes that communicate over one channel. The **residual session type** is the part of the protocol still to be performed at the current point. A session type is expressed from the provider endpoint's point of view; the client performs the complementary actions. The table describes what each side does as that shared protocol advances.

- **Before the request:**
  - Client: next, send request; then receive response and finish.
  - Provider: next, receive request; then send response and finish.
- **After the request is transferred:**
  - Client: next, receive response; then finish.
  - Provider: next, send response; then finish.
- **After the response is transferred:** both endpoints have only finishing left.
- **Protocol finished:** both endpoints are finished.

The arrows mean “then” and serve as explanatory notation for the sequence of actions; they are not OrgLang syntax. “Transferred” means both matching send/receive actions have taken place. Starting one side's action alone does not count as transfer. This is a conceptual trace showing how the shared protocol's residual state advances as each side performs its permitted action. A channel is not just a wire carrying arbitrary messages: its session type limits which interaction is allowed next.

**Connection to the implementation vocabulary:** at the process-expression level, the request and response correspond conceptually to complementary `Send`/`Recv` actions, followed by the protocol's finishing actions. Section 10 records the observed checker correspondence for `Send`, `Recv`, and `One`. The concrete OrgLang session-type expression is omitted because the exact typing rules and context updates remain to be established. Channel transfer (`Tensor`/`Lolli`) and labelled choice (`Plus`/`With`) are separate protocol forms discussed in Section 6.
## 4. Process declarations and definitions

Recall the recipe analogy from Section 2: a named process is like a recipe, and each run is an incarnation of that process. A **process declaration** describes the recipe's interface—the channels it expects, including one provider channel and any channels it uses as a client. A **process definition** supplies the implementation—the expression or process body that carries out the work. The distinction matters because the existence of a declaration alone leaves storage and loading of a usable body unverified. Go-specific names for these concepts are introduced in Part III.

### Definition, validation, and execution admission

**Agreed project contract:** A program version is admitted to execution only after its statically decidable well-formedness and type obligations have been checked. A failed static obligation is a static error, and the affected version is not admitted.

Keep three categories distinct in operation contracts:

- **Static obligation:** a property decidable from the program version and its available typing/name information at the admission boundary. Examples include arity, positional correspondence, and type compatibility when the relevant definitions and channel identities are statically known.
- **Runtime precondition:** a condition that depends on the current execution state or on a resource allocated during execution, such as whether a fresh incarnation can be created or whether a newly allocated identity is fresh.
- **Transition invariant:** a property that must hold across a successful state transition, such as preserving channel identity and protocol state or preventing observers from seeing a partial transition.

A condition belongs to the static category only when it is decidable at the specified admission boundary. If a target definition is introduced dynamically, its availability can be checked statically for the resulting program version at the point that version is admitted; availability at some later execution point must not be assumed without a corresponding versioning rule. Likewise, allocating a fresh runtime resource is not itself a static check, even if freshness is a required runtime invariant.

OrgLang programs may be further defined at runtime. A new fragment is checked against its expected type when it is defined. That fragment-level check does not replace checking the statically decidable obligations for the whole resulting program version before admission. Each operation's contract identifies its own static obligations, runtime preconditions, and transition invariants; this section defines the shared distinction rather than duplicating every operation-specific list.

This is the intended language-level contract recorded for this research. Whether and where the current implementation enforces it remains a separate implementation question.

## 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Named-process calls:** `ExternalCall` and `InternalCall` are the two named-process call forms described here. They differ in channel effects and continuation behavior. Both create a fresh process incarnation. `ExternalCall` creates a fresh provider channel and delivers it outward to the caller; `InternalCall` injects an existing channel inward into the new incarnation, transferring provider responsibility. Intended transitions are described in Section 7.

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The full constructor/field inventory is in Part III.

## 6. Session types: the protocol for a channel

A session type describes the allowed protocol from the provider endpoint's point of view; the type checker accounts for the client role when checking the other endpoint (Section 2). For the request/response example and residual session types, see Section 3.

A protocol can also pass a channel between processes. The sender gives the other process a channel it can use to communicate; the receiver gains access to that channel for the rest of its process. The implementation names the relevant session-type forms `Tensor` and `Lolli`. At a high level, these are the two complementary forms used to describe channel transfer together with the protocol that remains after the transfer. The names alone do not tell the reader which endpoint performs which action. Section 9 records the observed polarity assignments and checker coverage, while Section 10 describes the typing interface.

Protocols may also allow a choice between labelled alternatives: the implementation uses `Plus` and `With` for the two complementary type forms associated with such choices. `One` represents a finished protocol. The implementation contains `Up` and `Down` too, but their meaning in OrgLang is still being investigated; see Section 9 for observed checker coverage and Section 14 for open questions. The name `Link` is overloaded. **Type-level `Link`** is a session-type constructor referring to another type definition. At the process-expression level, the Go AST constructor is `LinkSpec`, which this document maps provisionally to **`InternalCall`** (Section 7).

Part III contains the constructor inventory, observed polarity assignments, checker coverage, and open questions.

## 7. Intended semantics of named-process calls

**This is the canonical statement of the intended language-level behavior.** Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

This section distinguishes two kinds of uncertainty:

- **Intended but underspecified:** the broad behavior is stated here, but its precise rule, conditions, or edge cases still need to be written down and checked.
- **Design question:** the available evidence does not settle which behavior or mechanism OrgLang should choose. Resolving it requires an explicit design decision.

Both named-process call forms resolve a named callee process and associate its declared channel parameters with supplied channels. They differ in what happens to the provider channel:

- **`ExternalCall`** reuses supplied client channels and creates a fresh provider channel for the new incarnation.
- **`InternalCall`** reuses an existing provider channel and the specified client channels, transferring them to the new incarnation.

**Shared failed-precondition atomicity rule:** For either call form, if a precondition fails before that operation commits, the operation does not expose a partial transition: the pre-state remains intact, with no partially transferred channel bindings and no new live incarnation exposed. This common rule does not define how a failure is reported or recovered from. The operations retain their distinct lifecycle contracts: `ExternalCall` has a bounded agreement-search phase before incarnation creation; `InternalCall` has a single successful atomic transition, with no cancellation phase. Runtime failures during or after a transition are not covered by this rule.

### `ExternalCall`

**Before:** the caller is executing an `ExternalCall` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Agreed project contract:** This section records the intended OrgLang contract agreed for this research. Correspondence with a published language specification and conformance with the current implementation are tracked separately.

**Static obligations and runtime preconditions:**

- At the admission boundary, the callee definition must be resolvable in the program version being checked.
- Each supplied client channel must match the type and position of the callee's corresponding client placeholder.
- Distinct formal client parameters must map to pairwise distinct existing channel identities.
- The caller's designated placeholder for the new provider channel must have a type compatible with the target process's provider protocol, accounting for the caller's client role.
- At execution time, the operation must be able to create a fresh incarnation with an identity that has never previously been allocated, and allocate a provider-channel identity that is fresh and distinct from all existing channels, including the supplied client channels.

**Static validation:** The shared rule in [Section 4](#4-process-declarations-and-definitions) applies. A channel/type mismatch, repeated channel identity, or invalid positional mapping is a static error when decidable from the program version and its channel-identity information at admission. Runtime allocation and freshness are runtime requirements, not static checks. The implementation's conformance remains unverified.

**Intended transition:**

1. Resolve the named callee process and map each formal client-channel parameter to the corresponding existing channel supplied by the call, in declaration order.
2. Ensure the static obligations listed above have been checked at the admission boundary, including strict session-type equality at both the target's client parameters and the caller's client-role placeholder for the new provider channel, under the applicable provider/client role convention. Session-type subtyping is out of scope for now. Check runtime preconditions when the relevant execution state and resources are available; they are not static validation.
3. Before creating the incarnation, search for a suitable pool agreement for the named process. The agreement-matching criterion, first-match selection, traversal order, escalation to manual intervention, and agreement-search timeout are specified as the process–pool boundary contract in [Process creation and pool selection, Sections 4.3–4.5](../about-spawn/README.md#43-search-order).
4. Once a suitable pool has been selected, create a fresh incarnation with its own execution state and a separate fresh provider channel, and associate the incarnation with that pool. Bind the new incarnation's client placeholders to the supplied channel identities and its provider placeholder to the fresh provider channel; designate that same fresh channel for delivery to the caller. The pool agreement automatically places the call under the selected pool's service; the agreement-search timeout and its boundary are specified in [about-spawn, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). Until the fresh provider channel is delivered to the caller, the supplied channels are held for the target and their protocol states remain unchanged, and the target cannot service the call or perform protocol actions or external effects on its behalf. Delivery is the commit point; the target may begin servicing only after delivery.

**After (intended):** the supplied client-channel identities and protocol states are preserved, but their use transfers to the new incarnation; the caller's continuation must not retain or use those same channel identities. The caller may retain channels not supplied to the call. Its continuation becomes eligible when it receives the fresh provider channel through the designated placeholder, and then uses that channel's client endpoint according to its protocol. The fresh provider channel is distinct from all supplied channels. General linearity and process-completion constraints from Section 2 still apply.

**Lifecycle and implementation status:** initiation, incarnation creation, provider-channel delivery, and the start of servicing are distinct events. **Agreed project decision:** the callee cannot begin servicing the call or perform protocol actions or external effects on its behalf before the fresh provider channel has been delivered to the caller. Delivery is the commit point; servicing may begin only after delivery. The caller's continuation becomes eligible on receipt of that channel, and after delivery the caller and callee may execute in either order or interleave, subject to protocol and linearity constraints. Before delivery, no protocol action or external effect associated with the call may occur; actions that cannot be fully undone are forbidden in this phase. The agreement-search timeout ends when a suitable agreement is found; if that happens before expiry, later engine work, including incarnation creation and channel delivery, is not governed by that timeout.

**Failure before commitment:** Delivery of the fresh provider channel to the caller remains the `ExternalCall` commit point. If the agreement-search timeout expires before a suitable agreement is found, the search ends without selecting a servicing pool; under the current working sequence, incarnation creation has not yet occurred, no provider channel is delivered, and the supplied client channels retain their original identities and protocol states with the caller. This is a pre-commit failure, not timeout-triggered cancellation of an already-created incarnation. The exact failure-reporting and recovery behavior remains unspecified. If a suitable agreement is found before timeout expiry, this timeout no longer applies: later engine work and provider-channel delivery may be delayed without triggering this search timeout. This is an intended language-level contract, not a claim that the current implementation provides this guarantee.

The pre-commit failure and delivery contract preserves these invariants:

- **Channel-state integrity:** if agreement search times out before finding a suitable agreement, supplied channel identities and protocol states remain unchanged with the caller.
- **Continuation eligibility:** the caller's continuation becomes eligible upon receipt of the fresh provider channel, as specified by the successful-call contract.
- **Commit boundary:** delivery is the commit point. The agreement-search timeout cannot cancel a call after a suitable agreement has been found, even if delivery is delayed.

General process/pool failure handling, recovery after a servicing incarnation fails, restart guarantees, and retry policy are outside the scope of this ExternalCall contract. In particular, this section makes no guarantee of recovery or successful completion after provider-channel delivery; it neither requires nor prohibits mechanisms that a separate fault-tolerance contract may define.

**Timeout configuration and scope:** The agreement-search timeout applies to `ExternalCall`, including escalation to the calling process's pool when the initial search finds no eligible pool. It stops governing the call once a suitable agreement is found; engine work after that point, including incarnation creation and provider-channel delivery, is outside this timeout. The timeout's source when no suitable agreement has yet been found, who configures or supplies it, and how it is represented remain open. The timeout policy does not guarantee eventual success or completion within a bounded time.

The inspected executor has no `ExternalCall` branch. The exact AST/runtime mapping among `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` remains open; this is an implementation-mapping question, not an unresolved choice about the intended positional channel contract. See [issue #85: Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893).

### `InternalCall`

**Before:** the invoking process provides a service on an existing channel (AST field `X`). The target process also receives a list of channels it will use as a client (AST field `Ys`). The terms *provider channel* and *client channels* describe the channel roles relative to the process being discussed. Both refer to the same underlying kind of channel resource. The role descriptions are explanatory labels. Runtime field resolution is documented separately in the implementation analysis.

**Static obligations and runtime preconditions:**

- At the admission boundary, the target definition must be resolvable in the program version being checked.
- The supplied channels must match the types and positions of the target's corresponding placeholders.
- The supplied channel identities must be pairwise distinct, including no overlap between `X` and `Ys`.
- `X` and `Ys` must account for **all channel identities bound in the invoking incarnation `P`**. After a successful call, no channel binding may remain attached to `P`.
- The binding environment of `P` follows the model-wide no-alias invariant: distinct bindings refer to distinct channel identities. This is not an `InternalCall`-specific condition.
**Static validation:** The shared rule in [Section 4](#4-process-declarations-and-definitions) applies. A channel/type mismatch, positional or arity mismatch, or repeated supplied channel identity (including overlap between `X` and `Ys`) is a static error when decidable at admission. The model-wide no-alias invariant applies here; it is not an additional `InternalCall` precondition. Set equality alone is not sufficient to establish that every binding in the environment has been transferred. The implementation's conformance remains unverified.

**Agreed channel-transfer and lifecycle decision:** On a successful transition, create a fresh incarnation `Q` at the start of the target definition, bind its provider placeholder to `X` and its client placeholders to `Ys` in declaration order, and remove those bindings from `P`. Because `X` and `Ys` account for the complete channel environment of `P`, the old incarnation semantically terminates without a language-level continuation. The precise atomicity, freshness, failure, and preservation invariants are consolidated below. This is the intended OrgLang behavior for this research document; conformance with the publication and current implementation is tracked separately.

**Irrevocable start and pool association:** Unlike `ExternalCall`, `InternalCall` has no pre-commit cancellation phase. Its successful atomic transition is the commit point: once the complete post-state is observable, the call has irreversibly begun, `P` has terminated, and the transferred channels belong to `Q`. `Q` is serviced by the same pool as `P`; `InternalCall` does not perform pool selection. The `ExternalCall` timeout/cancellation contract does not apply to `InternalCall`; there is no cancellation outcome that restores the transferred channel environment to `P`. A failure of a precondition before commit leaves the pre-state intact, as described below, but is not a committed call followed by cancellation. Behavior after a runtime failure during or after the transition remains outside this decision unless separately specified.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` has provider placeholder `x` bound to channel `c`, and client placeholder `y` bound to channel `d`. `Old` performs `InternalCall` to process `New`, passing `c` as `X` and `d` in `Ys`. The transition unbinds both placeholders in `Old` and binds `New`'s corresponding placeholders to `c` and `d`; the channel identities are preserved.

The atomicity and failure contract is stated precisely below. Pool association and selection are specified separately in [about-spawn, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing): `ExternalCall` selects a pool, while `InternalCall` uses the invoking incarnation's existing pool and does not select another one. Implementation questions are collected in [Section 14](#14-open-questions-and-next-tests).

**Atomicity boundary and failure behavior (intended contract):**

Treat the transition as a single state transition from a pre-state to a post-state, not as a sequence of externally observable mutations. Let the pre-state contain the live incarnation `P`, its complete channel environment, and the target definition. A successful transition produces a fresh `Q` whose provider placeholder is bound to `X` and whose client placeholders are bound to `Ys` in declaration order; `P` is no longer live and owns no channel bindings. Every transferred channel retains its identity and protocol state. No other incarnation's bindings or channel state change as a side effect of the transition.

The atomicity guarantee is about semantic observability, not a requirement that the implementation use a particular lock, transaction, or storage primitive. An implementation may perform internal preparation before committing the transition, provided that preparation is not observable as a live incarnation or as changed channel ownership. The commit point is the single point at which the complete post-state becomes observable.

If a precondition fails before the transition commits—for example, the target cannot be resolved, the channel arity or positional mapping is invalid, channel identities are duplicated, or a type obligation fails—the operation does not partially transfer ownership: `P` remains live with its original bindings and no new live `Q` is exposed. Error reporting and recovery after failures that occur during runtime execution are not yet specified; this contract must not be read as claiming crash consistency or rollback across process or machine failure.

**Required invariants (intended contract):**

- **Freshness:** `Q`'s incarnation identity has never been allocated to any incarnation in the execution history, including terminated incarnations. Incarnation identities are never reused.
- **Total transfer:** the invoking environment is injective, and the set of channel identities referenced by `P`'s bindings is exactly the set supplied by `X` and `Ys`; after commit, `P` has no channel bindings.
- **Exact rebinding:** each target placeholder is bound to the corresponding supplied channel identity, with `X` mapped to the provider placeholder and `Ys[i]` mapped to the i-th client placeholder.
- **Identity and protocol preservation:** transfer changes ownership/bindings, not channel identity or current session-protocol state.
- **Binding ownership:** after commit, none of the transferred bindings remain attached to `P`; each transferred identity is bound to exactly its designated placeholder in `Q`. This does not remove the peer endpoint's ordinary binding to the same channel.
- **All-or-nothing visibility:** observers see either the complete pre-state or the complete post-state, never a partial combination.

**Focused conformance tests to add:** The following are test obligations for the implementation, not claims that current tests already pass.

1. **Complete transfer:** use a target with one provider placeholder and multiple client placeholders; assert the target receives the exact channel identities in declaration order and the old incarnation is no longer live.
2. **Protocol-state preservation:** give each supplied channel a non-initial residual session state; assert the transition does not reset, advance, or replace that state.
3. **Fresh identity and non-reuse:** assert `Q` receives an identity never previously allocated, including identities of terminated incarnations; repeat transitions after termination to verify that no identity is reused.
4. **Duplicate identity rejection:** supply the same channel identity twice, including the `X`/`Ys` overlap case; assert rejection leaves the pre-state unchanged.
5. **Missing or extra channels:** mismatch the target's client-placeholder count; assert no partial binding and no live target incarnation.
6. **Atomic observation:** pause or instrument execution around the implementation's commit boundary; assert no observer can see `Q` with a subset of bindings or see both `P` and `Q` live with transferred ownership.
7. **Failure before commit:** force target resolution or validation to fail; assert `P` retains all original bindings and no partially initialized `Q` is observable.
8. **Unrelated-state isolation:** keep a separate incarnation and channel active; assert its bindings and protocol state are unchanged by the transition.

These tests should exercise the adapter, type checker, executor, and persistence/scheduling path together where those layers participate. A unit test of the AST constructor alone is insufficient evidence of conformance.
**Implementation status:** the inspected dispatcher has no `InternalCall` execution branch; execution and type-checking are unverified. See Section 14 for the unresolved lifecycle and representation questions.

### Boundary with pool semantics

Process invocation and incarnation creation are distinct from the pool mechanism that services a provider channel. Calls describe named-process and channel effects, while the pool's `Up … Down` protocol describes interaction through the pool's public channel. The pool's public channel belongs to the pool. Pool association, selection, and eligibility are pool-level concerns documented in [spawn-semantics, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing) and [Section 5](../about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel). Negotiation, reservation, failure behavior when no eligible pool exists, and resource provisioning remain underspecified. See also the [issue #85 proposal concerning the pool's offer channel](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672).

### `Fwd`

**Purpose:** redirect one specific interaction between two existing channels. This is an endpoint-level operation, not named-process invocation.

**Agreed project decision — one-shot forwarding under linearity:** `Fwd` redirects one interaction once and must not duplicate a linear endpoint. The publication's Example 9 illustrates redirecting an existing interaction; it does not require creating a second independent pending interaction.

If neither channel has a pending interaction, `Fwd` initiates one on the corresponding side according to forwarding direction and polarity. The exact mapping between polarity, side, and channel state remains open. The model rules out both channels having a pending interaction simultaneously.

**Implementation observation:** the inspected executor has paths for positive and negative polarity, but this does not establish that every path is reachable or correct. Neutral polarity takes an unexpected-polarity error path; a negative-polarity branch has a type-mismatch TODO; and the existing e2e `fwd` test has no result assertion. The pending-turn lookup checks `CommChnlPH`; handling a turn pending only on the other channel is unverified. The implementation therefore does not yet establish the complete transition contract.

The remaining rule must specify the reachable cases for positive and negative polarity when one side has a pending interaction, the treatment of neutral polarity, and the resulting continuation and one-shot consumption. Polarity is defined in Section 2; Section 9 records the checker's observed assignments. See Section 14 for the remaining question.

### Summary: compare the three operations

`ExternalCall` and `InternalCall` are the two named-process call forms, with different channel effects and continuation behavior. Record each operation's OrgLang meaning, publication interpretation, and implementation behavior separately. `ExternalCall` starts a named-process incarnation with a fresh provider channel and preserves a continuation for the caller; `InternalCall` starts a named-process incarnation, transfers all of the caller's channels to it, and semantically terminates the old incarnation; `Fwd` redirects one interaction between two existing channels, while named-process invocation is described by `ExternalCall` and `InternalCall`.

| Operation | Primary role | Intended control-flow effect | Intended channel effect | Semantic/evidential status | Implementation status |
|---|---|---|---|---|
| `ExternalCall` | Create and invoke a named-process incarnation with a fresh provider channel. | The caller's continuation becomes eligible only after it receives that channel. | Explicit parameter mapping; a fresh provider channel is delivered outward to the caller. | Agreed intended contract; operation-specific checks are described in Section 7, with shared validation timing in Section 4. Implementation mapping remains open. | Unverified; no executor branch found. |
| `InternalCall` | Create a named-process incarnation and transfer its channels. | The new incarnation starts at the beginning of its definition; the old incarnation semantically terminates. | All channels bound to the old incarnation are rebound to the new incarnation's typed placeholders, preserving channel identities. | Agreed intended contract; runtime representation open. | Unverified; no complete executor path found. |
| `Fwd` | Redirect one specific existing-channel interaction once. | No named-process incarnation or named-process continuation transfer is implied. | Redirects the relevant interaction; the operation must not duplicate a linear endpoint. | One-shot intent agreed; full transition rule remains open. | Partial; full symmetric behavior not established. |

Use this table as the quick comparison, and the operation-specific subsections above for the intended transitions and preconditions. Part II gives publication context; Part III records implementation evidence. Those evidence sources are not alternative definitions of the intended behavior.

## Part II. Comparison with the publication

## 8. Comparison with the supplied publication

The supplied publication gives the named-process call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here `p` names the definition, and the rule substitutes actual channel names for the corresponding formal names.

Table 4.2 likewise describes `a ← p b` as a call to named process `p`, which may communicate along channels `a` and `b`. This supports the reading of the publication construct as named-process invocation with channel substitution. It does not, by itself, establish OrgLang's complete `ExternalCall` contract or the runtime meaning of `ContExp`; those are project-level intended semantics documented in Section 7, with implementation conformance tracked separately.

Do not conflate named-process call with the separate cut/spawn rule `x ← P ; Q`. The latter has an inline process body `P`, a continuation `Q`, and explicitly allocates a fresh channel shared by the two resulting processes.

### The publication's cut/spawn rule

The publication separately describes cut/spawn as allocating a fresh channel shared by a spawned process and the original process's continuation. The detailed rule is documented in [about-spawn, Section 2.2](../about-spawn/README.md#22-existing-rationale-publication-cutspawn-rule); OrgLang's `Spawn` semantics remain a separate question.

The publication also gives the following forwarding rules. For clarity, the mode parameter `m` is omitted; this discussion focuses on forwarding.

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

The proposed correspondences between publication terms `msg` / `srv` and OrgLang terms `pub` / `sub` are recorded in the terminology table in Section 2; they remain provisional, not established synonyms. In the inspected implementation, `PubRec` stores a `ValExp` (publication/message action) and `SubRec` stores a `ContExp` (subscription/service continuation). The `Fwd` executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

### Reading the publication's forwarding example

The publication's Example 9 gives a concrete positive-polarity trace. A sender publishes the unit value `()` on `c`; a receiver is waiting on `d`; and a forwarding process connects the two. The receiver first becomes a service waiting on `d`. The forwarding process then produces a forwarding message for the pair `(d, c)`. When that forwarding message meets the service waiting on `d`, the service is redirected to wait on `c`; the sender's pending unit message can then be received, and the receiver continues as `P`.

The trace models forwarding as an interaction between a forwarding message and a waiting service. It keeps occurrences of `d` and `c` distinct except where a specific transition redirects an interaction. The trace also shows that the receiver may need another evaluation step to begin listening again after its service has been redirected.



## Part III. Implementation evidence and open questions

This part checks how the implementation corresponds to the language model and intended call contracts established in Parts I and II. Read the evidence in sequence: AST and type-checker coverage, representation and serialization, execution paths, then unresolved questions. Interpret each finding within its layer; end-to-end conclusions require evidence across layers.

## 9. Implementation map: process declarations and definitions

The main implementation locations inspected for this draft are:

- `proc/termdec/core/core.go`
- `proc/termdef/core/core.go`
- `proc/termexp/core/core.go`
- `proc/typeexp/core/core.go`
- `proc/compexec/core/core.go`
- `proc/termexp/adapter/tc.go`
- `proc/termexp/core/ds.go`

A process declaration is represented by `DecSpec`:

- `TermQN` — qualified name of the declaration.
- `LiabVar` — provider-channel placeholder.
- `AssetVars` — client-channel placeholders.

Section 7 defines the intended channel effects. The `CallSpec` source type contains `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, and a legacy `CommChnlPH` field marked `TODO удалить`. The adapter-level serialization discrepancies are detailed in Section 12; they do not establish end-to-end runtime behavior. For `InternalCall` (AST constructor `LinkSpec`), comments in `proc/termdec/core/core.go` suggest that `X` maps to the declaration's `LiabVar` and `Ys[i]` maps to `AssetVars[i]` in declaration order. The fields `X` and `Ys` are typed as `identity.ADT`, while placeholder names use `symbol.ADT`; the actual resolution path remains unverified.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/`Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so these types alone do not establish the persistence contract.

Related identifiers include:

- `TermQN`: qualified name associated with a declaration;- `ProcQN`: qualified name associated with a definition;
- `ProcTermQN`: name referenced by call/spawn expression constructors;
- expression identity / `valkey`: a candidate identifier for an expression incarnation, whose exact lifecycle remains to be confirmed.

Treat these identifiers as distinct unless their mapping is established.

### AST and session-type inventory

#### Process-expression AST inventory

The inspected process AST defines these constructors. Field names below are those observed in the Go AST; the short descriptions are provisional where noted.

- **`CloseSpec`** — `ContChnlPH`: close/terminate a session endpoint.
- **`WaitSpec`** — `ContChnlPH`, `ContExp`: wait on an endpoint, then continue.
- **`SendSpec`** — `CommChnlPH`, `ValChnlPH`: send a channel/value over a communication endpoint.
- **`RecvSpec`** — `CommChnlPH`, `NewChnlPH`, `ContExp`: receive and bind a channel, then continue.
- **`LabSpec`** — `CommChnlPH`, `ValLabQN`, `ContExp`: select/send a label; use of the AST continuation needs verification.
- **`CaseSpec`** — `CommChnlPH`, `ContExps`: offer branches indexed by labels.
- **`LinkSpec`** — `ProcTermQN`, `X`, `Ys` (`identity.ADT`): named-process construct without `ContExp`, unlike `CallSpec`.
- **`FwdSpec`** — `CommChnlPH`, `ContChnlPH`: forward between endpoints.
- **`CallSpec`** — `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, and legacy `CommChnlPH`: AST representation associated with `ExternalCall`. The constructor/field inventory is not evidence of runtime support; the concrete adapter discrepancies are recorded in Section 12.
- **`SpawnSpec`** — `CommChnlPH`, `ProcTermQN`, `NewChnlPHs`, `ContExp`: present in the AST; process semantics are deferred pending pool-level analysis.
- **`AcqureSpec`** — contract open; spelling preserved as in source.
- **`AcceptSpec`**, **`DetachSpec`**, **`ReleaseSpec`** — contracts open; see source for fields.

The table is a syntax inventory; execution support is assessed separately in Section 13.

#### Session-type AST and checker coverage

The process session-type AST contains these constructors; polarity below is what the inspected type checker records.

- **`OneSpec`** — no fields; positive polarity.
- **`TensorSpec`** — `Val`, `Cont`; positive polarity.
- **`LolliSpec`** — `Val`, `Cont`; negative polarity.
- **`PlusSpec`** — `Choices`; positive polarity.
- **`WithSpec`** — `Choices`; negative polarity.
- **`UpSpec`** — `Cont`; neutral polarity.
- **`DownSpec`** — `Cont`; neutral polarity.
- **Type-level `LinkSpec`** — `TypeQN`; neutral polarity.

The polarity assignments above are confirmed by inspection of `proc/typeexp/core/core.go`. They classify session types as positive, negative, or neutral; they do not define all operational cases.

At the AST level, process `Plus`/`With` choices are represented as label-indexed alternatives. The exact normalization and lookup rules for type references, and how `Up`/`Down` are unfolded, remain to be confirmed.

The process-level `CheckSpec` and `CheckRec` implementations explicitly handle only `One`, `Tensor`, `Lolli`, `Plus`, and `With`; other expected constructors reach the default panic. The pool-level conversion also includes `Link`, `Up`, and `Down`. This cross-layer difference is an implementation finding. Whether unresolved forms reach the process checker during ordinary execution remains an open question. Section 10 records the resulting open question.

One concrete source discrepancy exists in `pool/typeexp/core/tc.go`: the `DownSpec` conversion constructs and returns `UpRec` rather than `DownRec`. Also, the `PlusSpec` conversion composes a value key but does not check/return the `Compose` error in the same way as neighboring branches. These implementation findings require validation with focused tests and should remain separate from the intended type semantics.
## 10. Typing interface

### What type checking does

Before an expression is executed, the implementation checks whether the current channel protocols fit the operation. For example, a send action should only be used when the channel's current protocol permits sending; a close action should only be used when that interaction is ready to finish. These are intuitive explanations; complete formal rules remain to be established.

In the implementation, `proc/compexec/core/core.go` loads the current execution snapshot (a saved view of computation state at that execution point; its relationship to the publication's `configuration` and `environment` is not yet established), gathers relevant process declarations and type definitions, builds the type-checking context, and calls `checkType` before dispatching the expression. Its `LinearVars` map records the channel variables tracked by the checker. The exact invariants of this context remain unverified.

### How to read the correspondence table

The table records which session-type constructor the inspected checker expects for each process operator. “Provider-side” and “client-side” identify the two channel roles described in Section 2. A process as a whole still has one provider channel. A match in this table is evidence about the checker; the full language rule requires separate semantic evidence.
| Process operator | Provider-side expectation | Client-side expectation | Implementation evidence |
|---|---|---|---|
| `Send` | `Tensor` | `Lolli` | Confirmed as an observation about the inspected checker |
| `Recv` | `Lolli` | `Tensor` | Confirmed as an observation about the inspected checker |
| `Lab` | `Plus` | `With` | Confirmed as an observation about the inspected checker |
| `Case` | `With` | `Plus` | Confirmed as an observation about the inspected checker |
| `Close` / `Wait` | `One` on the corresponding endpoint side | `One` on the corresponding endpoint side | Unverified |
| `Fwd` | compatibility/polarity checks exist | full symmetric behavior not established | Partial |

These are checker observations. Complete typing rules still require side conditions, context splitting, substitution, and freshness conditions.

**Potential checker issue:** the `CaseSpec` branch in `proc/compexec/core/core.go` checks each choice using context maps that may be shared and mutated by recursive checks. A prior branch may therefore affect the next branch's starting context. This is a hypothesis that requires verification. Test multiple labels with distinct continuations and determine whether branch-local contexts or equivalent linear outcomes are required.

The constructor-coverage gap is described in Section 9. Whether normal execution resolves or unfolds `Link`, `Up`, and `Down` before the checker reaches this code remains open; see Section 14, item 6.

## 11. Execution and communication

At a high level, the inspected execution path follows six steps. The names in parentheses are implementation details:

1. Read the saved state of the computation (the execution snapshot).
2. Gather the process declarations and type definitions needed for the current action.
3. Check that the action fits the channel protocols currently in force (`checkType`).
4. Run the matching handler for the action (`takeWith`).
5. Save the resulting state changes and effects.
6. If the action produced a next expression, schedule or continue with it; otherwise return.

This outlines the observed path. The complete rules for blocking, resumption, and channel ownership remain to be established. Constructor-specific execution findings are in Section 13; representation gaps are in Section 12.

Communication may take more than one execution step. If the matching action from the other side is not yet available—for example, the corresponding `Wait` for a `Close`, or a receive for a send—the current action may register that it is waiting and return. When the other side becomes available, the implementation updates the exchange state and channel records, and may schedule the continuation. The precise ordering and ownership rules are still open.

The transition relation and invariants for publication (`pub`), subscription (`sub`), and exchange-turn state remain open; they require tracing the relevant producer and consumer paths together.

## 12. AST and serialization gaps

The adapter in `proc/termexp/adapter/tc.go` translates between AST, message, and stored representations. The findings below are source-level discrepancies; execution support is assessed separately in Section 13.

- `MsgFromExpSpec` has no branch for `CallSpec` (`ExternalCall`) or the process-expression AST constructor `LinkSpec` (`InternalCall`). A `CallSpec` passed through this conversion therefore reaches the adapter's unexpected-expression fallback rather than being serialized; `LinkSpec` does too.
- `MsgToExpSpec` does recognize the SDK `Call` kind, but reconstructs `CallSpec` by mapping `BindChnlPH` to `NewChnlPH` and copying `ProcTermQN` / `ValChnlPHs` only. It drops the AST's legacy `CommChnlPH` field and, importantly, `ContExp`; the AST therefore does not round-trip with its caller continuation through this adapter. The reverse converter has no `Link` case for `InternalCall`; if such a kind reaches the switch, it falls through to the unexpected-kind fallback. It also reconstructs `LabSpec` without its `ContExp`, although the AST contains that field.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in message-to-AST conversion and in stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.
- The stored process-expression representation also lacks a complete call/link shape: `ExpSpecDS` has payload fields for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`, but none for `CallSpec` or `LinkSpec`; its kind enum includes `LinkExp` and `SpawnExp`, but the process-level `dataFromExpSpec` / `dataToExpSpec` switches have no corresponding call/link branches. These conversions therefore cannot currently round-trip those constructors through this DTO layer.
- The process-level persistence components inspected here are incomplete independently of the conversion gaps: `proc/termexp/adapter/ds_pgx.go` implements `Repo.Insert` as a no-op, and `proc/termdef/adapter/ds_pgx.go` implements `Repo.InsertProc` as a no-op. The `proc/termdef` service's `Create` and `Retrieve` are also stubs. However, these are distinct from `proc/termdec` (which has concrete `AddRec` / retrieval queries) and `pool/termdef` (whose repository uses query-builder-backed inserts and reads). The inspected `proc/compexec` service loads process declarations through `proc/termdec` and executes a supplied expression; it does not itself establish that named `CallSpec` or `LinkSpec` is wired to the no-op `proc/termdef` path. Therefore these no-op components are a concrete gap, but their relevance to the active named-call route is still unverified.

These source-level discrepancies require focused tests and call-path analysis to establish their runtime impact. The executor-level findings and the limits of the available call-related test are summarized in Section 13.

## 13. What the execution path establishes

### Scope of the evidence

Use the status policy in Section 1 when reading the findings below. End-to-end behavior requires checking typing, adapters, scheduling, and execution together; AST presence or a single handler is not sufficient. The operation-specific gaps are collected in Section 14.

A formal reduction relation should distinguish at least:

- an expression that is ready to execute;
- an expression suspended while waiting for a peer;
- a communication whose peer has arrived;
- the resulting channel/linear-context update;
- continuation scheduling and persistence.

The current evidence supports treating execution as a stateful transition over an execution snapshot plus communication/exchange state. The snapshot may relate to the publication's `configuration` and `environment`, but that mapping remains an inference to verify. It does **not** yet justify importing a generic session-calculus semantics verbatim, nor asserting that each AST constructor has a complete reduction rule.

The first implementation-level transition descriptions should cover constructors whose typing and execution branches have both been checked end-to-end. For `ExternalCall`, `InternalCall`, and resource-management constructs, execution-path coverage and conformance to the intended contract in Section 7 remain unverified. `Spawn` is deferred to the pool-level analysis. Investigate `InternalCall` (AST constructor `LinkSpec`) alongside recursive process definitions and named-process invocation, while keeping its implementation analysis distinct from `Fwd`.

### Named-process calls: implementation evidence

This subsection records executor-level findings. Adapter discrepancies are listed in Section 12, and Section 14 consolidates the remaining questions.

**Implementation observation:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for the AST constructors `CallSpec` (`ExternalCall`), `SpawnSpec`, `LinkSpec` (`InternalCall`), `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. The type-checking path also has no `CallSpec` or `LinkSpec` case in either `checkProvider` or `checkClient`: after `Take` calls `checkType`, those expressions reach the checker's default panic rather than being accepted or rejected with a typed error. In addition, `LinkSpec.Via()` returns an empty placeholder, while `checkType` first uses `Via()` to look up the active linear channel and panics if it is absent. Thus the inspected path is blocked before the executor transition for both constructors; this is stronger evidence than a missing executor branch alone, but does not establish the intended typing rule. This observation describes the inspected implementation version; language design is documented separately.

The inspected `ExternalCall`-related `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The current process HTTP endpoint `POST /api/v1/procs/:id/steps` converts the supplied SDK step and calls `proc/compexec.API.Take`. That method runs `checkType` before `takeWith` and only then reaches the explicit transaction that calls `ModifyRec`; the checker’s default panic therefore occurs before this service’s execution-record modification step. The handler returns ordinary errors from `Take`, but has no local panic recovery. No conclusion is drawn here about whether outer Echo middleware recovers the panic, so the HTTP status/connection behavior remains unverified. Since `CallSpec` has no checker or executor branch, this inspected process-execution route does not implement `ExternalCall` even if the expression reaches it. Separately, `proc/termdef` service/repository operations are stubs, but the evidence does not establish that this storage path is used by the HTTP step route. The message-adapter and stored-DTO gaps in Section 12 add further obstacles to round-tripping a call. This is an implementation-evidence gap, not an unresolved choice about the intended channel contract in Section 7.
**Implementation observation:** `InternalCall` is represented by the process-expression AST constructor `LinkSpec`. Its `X` (provider channel) and `Ys` (client channels) are intended to identify caller-side channels. The AST types these fields as `identity.ADT` channel identifiers; placeholder names use `symbol.ADT`. No complete adapter or executor path was found. The AST `CallSpec` has an explicit `ContExp`; `LinkSpec` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This implementation-level API name alone cannot establish that OrgLang exposes a user-written `Spawn` operation. The repository contains three distinct `Spawn` representations; they should not be treated as one implementation:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but does not itself instantiate or attach a process body. The pool executor's separate `Take` route handles pool-level expressions (`Accept`, `Acquire`, `Apply`, `Hire`, `Detach`, `Release`); this does not supply the missing process-level `CallSpec` / `LinkSpec` transitions. Wiring the fresh channel described by the publication's cut rule is also not performed by `Spawn` itself.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape and belongs to a separate prototype. It does not establish behavior of the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This provides useful comparison context. Evidence that OrgLang exposes a standalone source-level `Spawn` remains unavailable. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

### Forwarding remains a separate open question

The inspected executor registers a `PubRec` carrying `FwdRec` when no turn is pending and polarity is positive, and a `SubRec` carrying `FwdRec` when polarity is negative. It also has paths for existing pending-turn records. These observations do not establish that all paths are reachable or correct. Neutral polarity follows an unexpected-polarity error path, one negative-polarity branch has a type-mismatch TODO, and the existing e2e `fwd` test has no result assertion. Complete runtime behavior remains unverified; see Section 14 for the contract questions.

## 14. Open questions and next tests

The list is ordered by investigation priority. Section 7 is the canonical statement of intended call semantics; the questions below concern unresolved details or evidence, not a request to restate that contract.

### Current implementation status at a glance

**Bottom line:** the inspected repository does not demonstrate a working end-to-end implementation of either named-process call form. This is not merely a missing test: both constructors lack checker and executor branches, and the inspected conversion/DTO paths cannot preserve their full representations. The available `ExternalCall` e2e scenario is disabled/inconclusive. Treat the call forms as specified intent, not as implemented behavior; the detailed evidence and its limits are in Sections 12–13.

The semantic decisions that should guide implementation are already recorded in Section 7: `ExternalCall` preserves supplied channel identities and protocol states while transferring their use to the target, and releases the caller continuation only when the fresh provider channel is received; `InternalCall` transfers the complete channel environment to a fresh incarnation and semantically terminates the old one. Model-wide non-aliasing and never-reused incarnation identities are settled assumptions. These decisions do not establish implementation conformance.

The remaining work falls into three different categories and should not be conflated:

- **Implementation blockers:** checker/executor support, lossless AST/message/DTO conversion, and a meaningful end-to-end test path for both call forms.
- **Other semantic questions:** the polarity/pending-turn cases for one-shot `Fwd` remain open.
- **Partly decided lifecycle design:** The language-level `ExternalCall` commit point and the pre-commit behavior when agreement search times out are specified here. The agreement-search timeout, including escalation, is documented in [about-spawn, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). The timeout's source when no suitable agreement is found, who configures it, and its representation remain open. These are intended semantics, not claims about implementation conformance.

A useful next validation milestone is one cohesive conformance suite: checker tests for accepted and rejected call shapes; adapter and persistence round-trip tests that preserve every constructor field and continuation; transition tests for identity freshness, channel non-aliasing, protocol-state preservation, old-incarnation termination, and continuation eligibility; plus a runnable end-to-end scenario with an actual target definition/body and asserted result. Add focused `ExternalCall` tests for agreement-search timeout, escalation within the same timeout, unchanged supplied channel identities and protocol states when no agreement is found, and the rule that engine delays after agreement discovery do not trigger the search timeout. General process/pool failure and post-delivery recovery tests belong to a future fault-tolerance scope. This suite is a proposed acceptance target, not a claim that tests currently exist or pass.

1. **ExternalCall implementation conformance:** Verify that the caller continuation becomes eligible only after receipt of the provider channel, not merely after the new incarnation starts. The inspected `checkProvider` / `checkClient` checker switches and `takeWith` executor switch have no `CallSpec` (`ExternalCall`) case; the checker reaches its default panic before the executor transition. The process-expression adapter also lacks a `MsgFromExpSpec` branch for `CallSpec`, while `MsgToExpSpec` drops `ContExp` when reconstructing a call. These gaps mean the repository evidence does not establish a complete call path or preservation of the caller continuation. Since `Take` checks types before its execution-record modification transaction, the observed checker panic occurs before that service's explicit `ModifyRec` step; HTTP panic recovery by outer middleware has not been verified. Add focused checker-error, adapter round-trip, and end-to-end conformance tests once the intended typing and transition contract are aligned.
2. **ExternalCall agreement-search timeout conformance:** The language-level commit point and pre-commit search-timeout behavior are specified in Section 7; the timeout policy is documented in [about-spawn, Section 4.5](../about-spawn/README.md#45-agreement-search-timeout). Remaining work is implementation conformance for the agreed contract. The timeout's source when no suitable agreement is found, who configures it, and its representation remain open.

   - Verify that agreement search, including escalation to the calling process's pool, is bounded by the same timeout.
   - Verify timeout expiry before finding a suitable agreement does not create an incarnation or deliver a provider channel, and leaves supplied client-channel identities and protocol states unchanged.
   - Verify that finding a suitable agreement ends the timeout's effect: subsequent engine delay before provider-channel delivery does not trigger this search timeout.
   - Verify that 

   General process/pool failures, recovery after delivery, restart guarantees, and retry policy are outside the current scope and may be addressed by a separate fault-tolerance contract.
3. **InternalCall implementation conformance:** Trace how `X` / `Ys` become bindings for the target's typed placeholders and how termination of `P` is represented. `LinkSpec.Via()` returns an empty placeholder, and `checkType` uses that value for a linear-channel lookup before entering `checkProvider` / `checkClient`; those checker switches and `takeWith` have no `LinkSpec` case. The inspected route therefore panics during checking rather than implementing an `InternalCall` transition. The process-expression adapter also has no `MsgFromExpSpec` branch for `LinkSpec` and no `Link` case in `MsgToExpSpec`; no complete adapter/executor path has been demonstrated. Add focused checker and adapter tests plus end-to-end conformance tests for the transition invariants in Section 7. The model-wide identity policy is settled: incarnation identities are never reused, including after termination. Implementation conformance to this policy remains unverified.
4. **Fwd transition rule (one-shot, linearity):** Specify the reachable positive- and negative-polarity cases when one side has a pending interaction, the treatment of neutral polarity, and the resulting continuation and one-shot consumption. The project decision is that `Fwd` redirects one specific interaction once and must not duplicate a linear endpoint. The publication's Example 9 supports redirecting an existing interaction and does not require a second independent pending interaction. If neither channel has a pending interaction, `Fwd` initiates one on the corresponding side according to forwarding direction and polarity; the exact mapping remains open. A pending interaction on both channels is impossible in the model. The inspected executor and e2e test do not establish the complete rule: neutral polarity follows an unexpected-polarity error path, one negative-polarity branch has a type-mismatch TODO, the pending-turn lookup checks `CommChnlPH`, and the e2e test has no result assertion. Add focused tests for the reachable cases and one-shot endpoint preservation.
5. **Representation and execution reachability:** Determine whether the conversion asymmetries in Section 12 are reachable, and test their runtime impact across adapter, executor, and scheduling paths.
6. **Type constructors and checker coverage:** Establish whether type-level `Link`, `Up`, and `Down` are resolved before the observed checker cases, and add tests for the intended coverage.
7. **Case branch-local linear contexts and continuations (project decisions):** Different `Case` branches may leave different linear contexts, provided each branch is individually linear; equivalent residual contexts across branches are not required. Check each branch continuation independently under the residual linear context produced by that branch. Do not merge or join the residual contexts of distinct branches as a typing precondition. Each reachable branch must still satisfy linearity and all applicable completion obligations within its own context. Verify that checking one branch cannot mutate the starting context of another. Add tests with multiple labels whose branches consume, retain, or advance different channels, and type-check each continuation under its own branch state.
8. **Linear context invariants:** Formalize the invariants for `ChnlBS`, provider/client orientation, and updates across operations. For `Case`, use the branch-local context and continuation rule in item 7. Define what constitutes a valid residual context, how each operation updates it, and how linear obligations are discharged on every reachable branch.
9. **Publication/subscription state:** Specify the transition semantics of publication, subscription, and exchange-turn records.
10. **Process creation:** Clarify the relationship among process-level invocation, pool-level `Spawn`, and the pool model, including the role of recursion through process definitions.
11. **Other constructors:** Specify the contracts of `Acqure`, `Accept`, `Detach`, and `Release`.

## 15. Non-goals

Pool and transaction semantics, resource-allocation policy, fairness, deadlock freedom, and a complete metatheory (such as preservation/progress) are deferred to a separate pass over the pool/transaction implementation.