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

**Linearity** is the channel usage/ownership discipline. **Model invariant:** channel bindings are non-aliasing: distinct bound channel placeholders refer to distinct channel identities. Consequently, distinct formal channel parameters supplied to a call must map to distinct existing channel identities. The no-alias property is a global assumption of the OrgLang model, not a special precondition introduced by `InternalCall`. A call's list of supplied identities covering the set of identities in an environment does not, by itself, establish completeness of the transfer; the environment's full set of bindings must still be accounted for. More generally, **normal completion** of a process is permitted only when its channel protocols permit completion and all linear obligations have been discharged; the inspected type checker rejects a normal-completion attempt while a provider-channel protocol remains unfinished; this is an implementation observation, not yet a complete formal language rule. This is distinct from `InternalCall`, whose agreed semantics terminate the old incarnation by transferring its complete channel environment to a replacement incarnation. That handoff is not evidence that the transferred protocols are finished. The full linearity invariant and its application across constructs remain open; do not infer them solely from `InternalCall`.

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
- **Transition invariant:** a property that must hold across a successful state transition, such as preserving channel identity and protocol state or preventing observers from seeing a partial handoff.

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

Both named-process call forms resolve a target process and associate its declared channel parameters with supplied channels. They differ in what happens to the provider channel:

- **`ExternalCall`** reuses supplied client channels and creates a fresh provider channel for the new incarnation.
- **`InternalCall`** reuses an existing provider channel and the specified client channels, transferring them to the new incarnation.

### `ExternalCall`

**Before:** the caller is executing an `ExternalCall` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Agreed project contract:** This section records the intended OrgLang contract agreed for this research. Correspondence with a published language specification and conformance with the current implementation are tracked separately.

**Static obligations and runtime preconditions:**

- At the admission boundary, the target definition must be resolvable in the program version being checked.
- Each supplied client channel must match the type and position of the target's corresponding client placeholder.
- Distinct formal client parameters must map to pairwise distinct existing channel identities.
- The caller's designated placeholder for the new provider channel must have a type compatible with the target process's provider protocol, accounting for the caller's client role.
- At execution time, the operation must be able to create a fresh incarnation with an identity that has never previously been allocated, and allocate a provider-channel identity that is fresh and distinct from all existing channels, including the supplied client channels.

**Static validation:** The shared rule in [Section 4](#4-process-declarations-and-definitions) applies. A channel/type mismatch, repeated channel identity, or invalid positional mapping is a static error when decidable from the program version and its channel-identity information at admission. Runtime allocation and freshness are runtime requirements, not static checks. The implementation's conformance remains unverified.

**Intended transition:**

1. Resolve the named process and map each formal client-channel parameter to the corresponding existing channel supplied by the call, in declaration order.
2. Ensure the static obligations listed above have been checked at the admission boundary, including session-type compatibility at both the target's client parameters and the caller's client-role placeholder for the new provider channel. The precise compatibility relation remains to be formalized. Check runtime preconditions when the relevant execution state and resources are available; they are not static validation.
3. After the required static obligations pass and the program version is admitted, initiate the call. While service is pending, the supplied channels are held for the target and their protocol states remain unchanged.
4. On successful service, create a fresh incarnation with its own execution state, bind its client placeholders to the supplied channel identities, and create a separate fresh provider channel for the target's provider placeholder and the caller's designated placeholder.

**After (intended):** the supplied client-channel identities and protocol states are preserved, but their use transfers to the new incarnation; the caller's continuation must not retain or use those same channel identities. The caller may retain channels not supplied to the call. Its continuation becomes eligible when it receives the fresh provider channel through the designated placeholder, and then uses that channel's client endpoint according to its protocol. The fresh provider channel is distinct from all supplied channels. General linearity and process-completion constraints from Section 2 still apply.

**Lifecycle and implementation status:** the operation passes through initiated, pending, and serviced stages. During the pending stage, the reservation and protocol-state rules described above apply; “reserved” denotes semantic exclusion of competing use, not a required lock or storage mechanism. What happens to the supplied bindings if service fails or the call is cancelled—including whether and how they are returned to the caller—remains unspecified. Every successful service creates a fresh incarnation. After service, caller and callee may execute in either order or interleave, subject to protocol and linearity constraints. The caller's continuation depends on receipt of the provider channel, not on callee termination.

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

**Agreed channel-transfer and lifecycle decision:** On a successful handoff, create a fresh incarnation `Q` at the start of the target definition, bind its provider placeholder to `X` and its client placeholders to `Ys` in declaration order, and remove those bindings from `P`. Because `X` and `Ys` account for the complete channel environment of `P`, the old incarnation semantically terminates without a language-level continuation. The precise atomicity, freshness, failure, and preservation invariants are consolidated below. This is the intended OrgLang behavior for this research document; conformance with the publication and current implementation is tracked separately.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` has provider placeholder `x` bound to channel `c`, and client placeholder `y` bound to channel `d`. `Old` performs `InternalCall` to process `New`, passing `c` as `X` and `d` in `Ys`. The handoff unbinds both placeholders in `Old` and binds `New`'s corresponding placeholders to `c` and `d`; the channel identities are preserved.

The atomicity and failure contract is stated precisely below. Pool association and selection are specified separately in [spawn-semantics, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing); implementation questions are collected in [Section 14](#14-open-questions-and-next-tests).

**Atomicity boundary and failure behavior (intended contract):**

Treat the handoff as a single state transition from a pre-state to a post-state, not as a sequence of externally observable mutations. Let the pre-state contain the live incarnation `P`, its complete channel environment, and the target definition. A successful transition produces a fresh `Q` whose provider placeholder is bound to `X` and whose client placeholders are bound to `Ys` in declaration order; `P` is no longer live and owns no channel bindings. Every transferred channel retains its identity and protocol state. No other incarnation's bindings or channel state change as a side effect of the handoff.

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
2. **Protocol-state preservation:** give each supplied channel a non-initial residual session state; assert the handoff does not reset, advance, or replace that state.
3. **Fresh identity and non-reuse:** assert `Q` receives an identity never previously allocated, including identities of terminated incarnations; repeat handoffs after termination to verify that no identity is reused.
4. **Duplicate identity rejection:** supply the same channel identity twice, including the `X`/`Ys` overlap case; assert rejection leaves the pre-state unchanged.
5. **Missing or extra channels:** mismatch the target's client-placeholder count; assert no partial binding and no live target incarnation.
6. **Atomic observation:** pause or instrument execution around the implementation's commit boundary; assert no observer can see `Q` with a subset of bindings or see both `P` and `Q` live with transferred ownership.
7. **Failure before commit:** force target resolution or validation to fail; assert `P` retains all original bindings and no partially initialized `Q` is observable.
8. **Unrelated-state isolation:** keep a separate incarnation and channel active; assert its bindings and protocol state are unchanged by the handoff.

These tests should exercise the adapter, type checker, executor, and persistence/scheduling path together where those layers participate. A unit test of the AST constructor alone is insufficient evidence of conformance.

**Implementation status:** the inspected dispatcher has no `InternalCall` execution branch; execution and type-checking are unverified. See Section 14 for the unresolved lifecycle and representation questions.

### Boundary with pool semantics

Process invocation and incarnation creation are distinct from the pool mechanism that services a provider channel. Calls describe named-process and channel effects, while the pool's `Up … Down` protocol describes interaction through the pool's public channel. The pool's public channel belongs to the pool. Pool association, selection, and eligibility are pool-level concerns documented in [spawn-semantics, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing) and [Section 5](../about-pools-and-transaction-types/README.md#5-the-pools-public-transaction-channel). Negotiation, reservation, failure behavior when no eligible pool exists, and resource provisioning remain underspecified. See also the [issue #85 proposal concerning the pool's offer channel](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672).

### `Fwd`

**Purpose:** connect one specific interaction on one existing channel to the corresponding interaction on another. This is an endpoint-level operation on existing channels, not named-process invocation.

**Agreed project decision — one-shot forwarding under linearity:** `Fwd` redirects a particular interaction once; it does not create a persistent alias or an ongoing link between the two channel identities. The forwarding operation must not duplicate a linear endpoint, make two channel bindings denote the same channel identity, or leave a reusable alias after the particular redirection has completed. The channel identities remain distinct; the transition redirects the relevant pending interaction/service rather than globally renaming channels. This decision fixes the intended direction, but does not yet specify every transition case.

The publication illustrates a positive-polarity case with a unit message pending on `c` and a receiver waiting on `d`; see Section 8 for the trace. A complete rule is still needed for positive, negative, and neutral polarity, for when either or both sides have pending turns (including when neither does yet), and for the precise continuation/consumption state before and after the one-shot redirection. Polarity is defined in Section 2; Section 9 records the checker's observed assignments. The implementation's turn-like records appear to represent pending communication/exchange state, but `turn` is not used here as a synonym for a communication step. The publication example and inspected executor do not settle all cases; see Section 14 for the remaining question.

### Summary: compare the three operations

`ExternalCall` and `InternalCall` are the two named-process call forms, with different channel effects and continuation behavior. Record each operation's OrgLang meaning, publication interpretation, and implementation behavior separately. `ExternalCall` starts a named-process incarnation with a fresh provider channel and preserves a continuation for the caller; `InternalCall` starts a named-process incarnation, transfers all of the caller's channels to it, and semantically terminates the old incarnation; `Fwd` connects two existing channel interactions, while named-process invocation is described by `ExternalCall` and `InternalCall`.

| Operation | Primary role | Intended control-flow effect | Intended channel effect | Semantic/evidential status | Implementation status |
|---|---|---|---|---|
| `ExternalCall` | Create and invoke a named-process incarnation with a fresh provider channel. | The caller's continuation becomes eligible only after it receives that channel. | Explicit parameter mapping; a fresh provider channel is delivered outward to the caller. | Agreed intended contract; operation-specific checks are described in Section 7, with shared validation timing in Section 4. Implementation mapping remains open. | Unverified; no executor branch found. |
| `InternalCall` | Create a named-process incarnation and transfer its channels. | The new incarnation starts at the beginning of its definition; the old incarnation semantically terminates. | All channels bound to the old incarnation are rebound to the new incarnation's typed placeholders, preserving channel identities. | Agreed intended contract; runtime representation open. | Unverified; no complete executor path found. |
| `Fwd` | Redirect one specific existing-channel interaction once. | No named-process incarnation or named-process continuation transfer is implied; no persistent alias remains. | Redirects the relevant interaction without merging channel identities or duplicating linear endpoints. | One-shot/non-aliasing intent agreed; full transition rule remains open. | Partial; full symmetric behavior not established. |

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

- `TermQN`: qualified name associated with a declaration;
- `ProcQN`: qualified name associated with a definition;
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

- `MsgFromExpSpec` has no branch for `CallSpec` (`ExternalCall`) or the process-expression AST constructor `LinkSpec` (`InternalCall`). A `CallSpec` passed through this conversion therefore reaches the adapter's unexpected-expression fallback rather than being serialized.
- `MsgToExpSpec` reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. It also reconstructs `LabSpec` without its `ContExp`, although the AST contains that field.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in message-to-AST conversion and in stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.

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

The first fully formalized implementation-level rules should cover constructors whose typing and execution branches have both been checked end-to-end. Complete implementation-level reduction rules for `ExternalCall`, `InternalCall`, and resource-management constructs await verification of their execution paths and reconciliation with the intended contract in Section 7. `Spawn` is deferred to the pool-level analysis. Investigate `InternalCall` (AST constructor `LinkSpec`) alongside recursive process definitions and named-process invocation, while keeping its analysis distinct from `Fwd`.

### Named-process calls: implementation evidence

This subsection records executor-level findings. Adapter discrepancies are listed in Section 12, and Section 14 consolidates the remaining questions.

**Implementation observation:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for the AST constructors `CallSpec` (`ExternalCall`), `SpawnSpec`, `LinkSpec` (`InternalCall`), `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. This observation describes the inspected dispatcher version; language design is documented separately.

The inspected `ExternalCall`-related `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The process-definition persistence methods inspected so far also appear to be stubs. Combined with the adapter gaps in Section 12 and the missing executor branch noted above, the repository evidence does not demonstrate a successful `ExternalCall` transition. This is an implementation-evidence gap, not an unresolved choice about the intended channel contract in Section 7.

**Implementation observation:** `InternalCall` is represented by the process-expression AST constructor `LinkSpec`. Its `X` (provider channel) and `Ys` (client channels) are intended to identify caller-side channels. The AST types these fields as `identity.ADT` channel identifiers; placeholder names use `symbol.ADT`. No complete adapter or executor path was found. The AST `CallSpec` has an explicit `ContExp`; `LinkSpec` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This implementation-level API name alone cannot establish that OrgLang exposes a user-written `Spawn` operation. The repository contains three distinct `Spawn` representations; they should not be treated as one implementation:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode. Instantiating a process body and wiring the fresh channel described by the publication's cut rule are separate steps that this method does not perform.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape and belongs to a separate prototype. It does not establish behavior of the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This provides useful comparison context. Evidence that OrgLang exposes a standalone source-level `Spawn` remains unavailable. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

### Forwarding remains a separate open question

The executor contains a `Fwd` branch. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. The code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads; their switches contain no handling for `FwdRec`. It remains unverified whether another part of scheduling and exchange handling covers this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken.

A formal reduction rule should be added after the relevant typing, executor, adapter, and scheduling paths have been checked together.

## 14. Open questions and next tests

The list is ordered by investigation priority. Section 7 is the canonical statement of intended call semantics; the questions below concern unresolved details or evidence, not a request to restate that contract.

1. **ExternalCall implementation conformance:** Verify that the caller continuation becomes eligible only after receipt of the provider channel, not merely after the new incarnation starts. The inspected executor has no `ExternalCall` branch; a complete runtime path and focused conformance test are still needed.
2. **ExternalCall failure lifecycle and representation (semantics unresolved):** If service fails or the call is cancelled while client channels are reserved for the target, it is not yet defined whether the call waits/retries with the channels still reserved, fails and restores the original bindings to the caller, or distinguishes temporary unavailability from explicit failure/cancellation and restores bindings only in the latter cases. These choices affect whether the caller can continue, who owns the linear channels, and whether retries can safely reuse them; do not assume any option is the language contract. Resolve this by specifying observable failure/cancellation outcomes and channel ownership for each terminal/nonterminal path, then test the transition model. Separately trace how `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` are resolved and represented through the adapter and runtime; implementation evidence does not decide the intended semantics.
3. **InternalCall implementation conformance and open design point:** Trace how `X` / `Ys` become bindings for the target's typed placeholders and how termination of `P` is represented. Add end-to-end tests for the transition invariants in Section 7. The model-wide identity policy is settled: incarnation identities are never reused, including after termination. Implementation conformance to this policy remains unverified.
4. **Fwd transition rule (one-shot, linearity):** The project decision is that `Fwd` redirects one specific interaction once and does not establish a persistent channel alias. Preserve distinct channel identities and linear ownership; do not duplicate endpoints or globally rename channels. Still specify the transitions for positive, negative, and neutral polarity, including no pending turn, one-sided pending turns, matching/mismatched pending-turn kinds, and the resulting continuation/turn consumption. The publication example and inspected executor do not settle all cases. Add focused tests for one-shot completion, absence of a residual alias, endpoint non-duplication, and each polarity/turn combination.
5. **Representation and execution reachability:** Determine whether the conversion asymmetries in Section 12 are reachable, and test their runtime impact across adapter, executor, and scheduling paths.
6. **Type constructors and checker coverage:** Establish whether type-level `Link`, `Up`, and `Down` are resolved before the observed checker cases, and add tests for the intended coverage.
7. **Case branch-local linear contexts (project decision; continuation rule open):** Different `Case` branches may leave different linear contexts, provided each branch is individually linear. Do not require all branches to preserve equivalent residual linear contexts merely because they share a `Case`. The typing rule for the continuation after `Case` remains unresolved: specify whether the continuation is checked separately under each selected branch's residual context, whether the syntax/typing model represents branch-dependent continuations explicitly, or whether some join/compatibility condition is required. Verify that checking one branch cannot accidentally mutate the starting context of another. Add tests with multiple labels whose branches consume, retain, or advance different channels, and check the continuation under every reachable branch state.
8. **Linear context invariants:** Formalize the invariants for `ChnlBS`, provider/client orientation, and updates across operations. For `Case`, the project decision permits different individually linear residual contexts across branches; the continuation-typing rule is tracked separately in item 7. Define what constitutes a valid residual context and how each operation updates it.
9. **Publication/subscription state:** Specify the transition semantics of publication, subscription, and exchange-turn records.
10. **Process creation:** Clarify the relationship among process-level invocation, pool-level `Spawn`, and the pool model, including the role of recursion through process definitions.
11. **Other constructors:** Specify the contracts of `Acqure`, `Accept`, `Detach`, and `Release`.

## 15. Non-goals

Pool and transaction semantics, resource-allocation policy, fairness, deadlock freedom, and a complete metatheory (such as preservation/progress) are deferred to a separate pass over the pool/transaction implementation.

