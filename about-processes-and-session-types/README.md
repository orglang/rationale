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

For example, a project decision can confirm the intended direction of OrgLang behavior while implementation coverage remains unverified. Identify that decision as the source and state what it establishes; authoritative language status requires the appropriate language evidence.

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

The correspondence between OrgLang, the publication, and implementation identifiers is tracked separately in the terminology table. Its mapping status describes the correspondence, not the certainty of an individual claim or the completeness of the implementation.

Use **Confirmed**, **Provisional**, or **Unresolved** for mappings:

- **Confirmed** — the correspondence is supported by sufficient evidence.
- **Provisional** — evidence supports the correspondence, but it still needs verification.
- **Unresolved** — no correspondence is established, or sources appear to conflict. Describe any discrepancy in the mapping table's **Notes** column.

Record mismatches explicitly; treat similarly named concepts as equivalent only when evidence supports that mapping.

## 2. Core concepts

OrgLang processes communicate through **channels**. A channel connects two roles: the **provider**, which offers a service, and the **client**, which uses it. Each participant has an **endpoint**; the same channel is the provider channel for one process and the client channel for the other. These roles are relative to each process's perspective. Each process has one provider channel of its own and may use other channels as a client. The two named-process call forms are **`ExternalCall`** and **`InternalCall`**. Both create a fresh process incarnation, but transfer channels in different directions relative to that incarnation.

**Process** is the general umbrella term in this document; its precise referent follows context. A **named process** is the process identified by a name. A **process declaration** describes its interface, while a **process definition** supplies its behavior. Each start creates a concrete running copy called a **process incarnation**. Each term refers to a distinct concept. A **channel placeholder** is a syntactic name in an expression or process interface that stands for a channel. An environment or substitution associates the name with the relevant channel resource or endpoint. The implementation may represent these layers with different Go types, and the mapping must be verified rather than inferred from field names alone.

A **session type** describes the allowed protocol from the provider endpoint's point of view. When checking the client endpoint, the type checker accounts for the client role and the complementary actions it permits. A **residual session type** is the remaining part of that protocol after prior interaction steps. The request/response example and the meaning of a **residual session type** are introduced in Section 3.

**Linearity** is the channel usage/ownership discipline. **Intended linearity rule:** distinct formal channel parameters must map to distinct existing channel identities. The complete formal invariant and the implementation layer enforcing it remain to be established. More generally, a process may finish only when its channel protocols permit completion and all linear obligations have been discharged; the type checker rejects an attempted completion while a provider-channel protocol remains unfinished. The full invariant and its application across constructs remain open; do not infer them solely from `InternalCall`.

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
| Linearity | Channel usage/ownership discipline; distinct formal channel parameters must map to distinct existing channels, and process completion requires all linear obligations to be discharged. The full formal invariant remains to be written down. |
| Polarity | An implementation-level positive/negative/neutral classification used by the type checker; operational consequences are documented separately. |
| Snapshot | An implementation concept that may relate to the publication's `configuration` and `environment`; the exact mapping remains open. |
| Turn | The implementation uses turn-like records for pending communication/exchange state; their language-level status and precise semantics remain open. |

### Terminology correspondence: OrgLang, publication, and implementation

Use one row for one proposed correspondence. **Mapping status** describes the strength of that correspondence, not the evidence status of a claim or the implementation status. Apply the mapping-status definitions in [Section 1](#1-scope-and-evidence).

| OrgLang term / concept | Publication term / notation | Implementation name | Mapping status | Notes |
|---|---|---|---|---|
| Provider channel placeholder | Provider-role channel parameter in the process interface | `LiabVar` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| Client channel placeholders | Client-role channel parameters in the process interface | `AssetVars` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| `InternalCall` provider channel (`X`) | No equivalent established in the inspected excerpt | `LinkSpec.X` (AST spelling: process-expression constructor `LinkSpec`) | Unresolved | Intended to denote the existing provider channel, but the field is typed as `identity.ADT`, not a channel-placeholder symbol. Runtime resolution is unverified. |
| `InternalCall` client channels (`Ys`) | No equivalent established in the inspected excerpt | `LinkSpec.Ys` (AST constructor: `LinkSpec`) | Unresolved | Intended to denote client channels in declaration order; representation and runtime resolution are unverified. |
| `ExternalCall` | `a ← p b`; publication substitution rule | `CallSpec`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, `NewChnlPH` | Provisional | Publication supports invocation and substitution; see Section 7 for the intended contract and Section 14 for unresolved details. Implementation mapping remains unverified. |
| `InternalCall` | No equivalent established | `LinkSpec` (implementation AST spelling `Link`) | Unresolved | Intended to transfer an existing channel into a fresh incarnation and transfer provider responsibility to it; no complete adapter/executor path was found. |
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

The arrows mean “then” and serve as explanatory notation for the sequence of actions; they are not OrgLang syntax. “Transferred” means the matching send/receive actions have both taken place, not merely that one side has started its action. This is a conceptual trace showing how the shared protocol's residual state advances as each side performs its permitted action. A channel is not just a wire carrying arbitrary messages: its session type limits which interaction is allowed next.

**Connection to the implementation vocabulary:** at the process-expression level, the request and response correspond conceptually to complementary `Send`/`Recv` actions, followed by the protocol's finishing actions. Section 10 records the observed checker correspondence for `Send`, `Recv`, and `One`. The concrete OrgLang session-type expression is omitted because the exact typing rules and context updates remain to be established. Channel transfer (`Tensor`/`Lolli`) and labelled choice (`Plus`/`With`) are separate protocol forms discussed in Section 6.

## 4. Process declarations and definitions

Recall the recipe analogy from Section 2: a named process is like a recipe, and each run is an incarnation of that process. A **process declaration** describes the recipe's interface—the channels it expects, including one provider channel and any channels it uses as a client. A **process definition** supplies the implementation—the expression or process body that carries out the work. The distinction matters because the existence of a declaration alone leaves storage and loading of a usable body unverified. Go-specific names for these concepts are introduced in Part III.

## 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Named-process calls:** `ExternalCall` and `InternalCall` are the two named-process call forms described here. They differ in channel effects and continuation behavior. Both create a fresh process incarnation. `ExternalCall` creates a fresh provider channel and delivers it outward to the caller; `InternalCall` injects an existing channel inward into the new incarnation, transferring provider responsibility. Intended transitions are described in Section 7.

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The full constructor/field inventory is in Part III.

## 6. Session types: the protocol for a channel

A session type describes the allowed protocol from the provider endpoint's point of view; the type checker accounts for the client role when checking the other endpoint (Section 2). For the request/response example and residual session types, see Section 3.

A protocol can also pass a channel between processes. The sender gives the other process a channel it can use to communicate; the receiver gains access to that channel for the rest of its process. The implementation names the relevant session-type forms `Tensor` and `Lolli`. At a high level, these are the two complementary forms used to describe channel transfer together with the protocol that remains after the transfer. The names alone do not tell the reader which endpoint performs which action: Section 9 records the observed polarity assignments and checker coverage, while Section 10 describes the typing interface. The exact direction mapping is reserved for Section 9, where the observed polarity assignments and checker coverage are recorded.

Protocols may also allow a choice between labelled alternatives: the implementation uses `Plus` and `With` for the two complementary type forms associated with such choices. `One` represents a finished protocol. The implementation contains `Up` and `Down` too, but their meaning in OrgLang is still being investigated; see Section 9 for observed checker coverage and Section 14 for open questions. The name `Link` is overloaded: **type-level `Link`** is a session-type constructor referring to another type definition; at the process-expression level, the Go AST constructor is `LinkSpec`, corresponding to the semantic operation **`InternalCall`** (Section 7).

Part III contains the constructor inventory, observed polarity assignments, checker coverage, and open questions.

## 7. Intended semantics of named-process calls

**This is the canonical statement of the intended language-level behavior.** Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

This section distinguishes two kinds of uncertainty:

- **Intended but underspecified:** the broad behavior is stated here, but its precise rule, conditions, or edge cases still need to be written down and checked.
- **Design question:** the available evidence does not settle which behavior or mechanism OrgLang should choose. Resolving it requires an explicit design decision.

Both named-process call forms resolve a target process and associate its declared channel parameters with channels supplied by the call. The form-specific contract determines which channels are reused and whether a fresh provider channel is created: `ExternalCall` supplies existing client channels and creates a fresh provider channel; `InternalCall` passes an existing provider channel and its specified client channels to the new incarnation.


### `ExternalCall`

**Before:** the caller is executing an `ExternalCall` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Agreed project contract:** This section records the intended OrgLang contract agreed for this research. Correspondence with a published language specification and conformance with the current implementation are tracked separately.

For `ExternalCall`, resolve the named process and explicitly bind each formal client-channel parameter to an existing channel supplied in the call's environment/arguments. Type checking must verify that each supplied channel's current session type is compatible with the session type required by its corresponding formal parameter, accounting for the roles of the caller and the formal parameter. It must also verify that the provider-oriented session type associated with the new incarnation's provider channel is compatible with the provider-oriented session type assigned to the caller's channel placeholder, accounting for the caller's client role. The exact compatibility rules remain to be formalized. Then start a fresh incarnation with its own execution state and channel environment. Formal parameter names are local to that incarnation; the mapping associates them with existing channel identities. The mapped channels are transferred for use by the new incarnation, and a separate fresh provider channel connects it to the caller.

**After (intended):** the caller's continuation becomes eligible when it receives the fresh provider channel through the designated placeholder. The caller then uses the client endpoint according to that channel's protocol. The mapped channels retain their identities and protocol states, while their use transfers to the new incarnation; the fresh provider channel is distinct from them. General linearity and process-completion constraints from Section 2 still apply.

**Lifecycle and implementation status:** the operation passes through initiated, pending, and serviced stages. While pending, mapped channels are held for the new incarnation and their protocol state remains unchanged. Every successful service creates a fresh incarnation. The caller and callee may then execute in either order or interleave, subject to protocol and linearity constraints; the caller's continuation depends on receipt of the provider channel, not on callee termination. The inspected executor has no `ExternalCall` branch, and the exact mapping among `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` remains open. See [issue #85: Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893).

### `InternalCall`

**Before:** the invoking process provides a service on an existing channel (AST field `X`). The target process also receives a list of channels it will use as a client (AST field `Ys`). The terms *provider channel* and *client channels* describe the channel roles relative to the process being discussed. Both refer to the same underlying kind of channel resource. The role descriptions are explanatory labels, not claims about how the runtime resolves the fields.

**Preconditions (provisional):** the target process definition must be available and a fresh incarnation must be creatable. Whether channel/protocol compatibility is required, and where it is checked, remain open.

**Provisional intended contract:** start a fresh incarnation of the named process, passing the existing provider channel as its provider channel and the specified client channels in declaration order. Transfer provider-side responsibility for the existing provider channel to the new incarnation.

**After (intended):** the new incarnation assumes provider responsibility for the existing channel, and the old incarnation has no ordinary continuation. The old incarnation's runtime lifecycle—termination, suspension, or retention as a runtime record—remains open.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` provides channel `c`, and the client has already sent a request. `Old` performs `InternalCall` to process `New`, passing `c`. The intended handoff transfers provider responsibility for `c` to `New`.

**Atomic handoff (provisional contract):** The intended transition creates the new incarnation and transfers the specified channels as one semantic transition. The target incarnation becomes observable as part of that completed handoff. Implementation atomicity and the representation of the old incarnation remain unverified. Pool association and selection are specified separately in [spawn-semantics, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing); open lifecycle questions are collected in [Section 7](../about-spawn/README.md#7-open-questions-and-deferred-topics).

**Implementation status:** the inspected dispatcher has no `InternalCall` execution branch; execution and type-checking are unverified. See Section 14 for the unresolved lifecycle and representation questions.

### Boundary with pool semantics

Process invocation and incarnation creation are distinct from the pool mechanism that services a provider channel. Calls describe named-process and channel effects, while the pool's `Up … Down` protocol describes interaction through the pool's public channel. The pool's public channel belongs to the pool. Pool association, selection, and eligibility are pool-level concerns documented in [spawn-semantics, Section 4](../about-spawn/README.md#4-pool-selection-and-servicing) and [Section 5](../about-spawn/README.md#5-the-pools-public-channel). Negotiation, reservation, failure behavior when no eligible pool exists, and resource provisioning remain underspecified. See also the [issue #85 proposal concerning the pool's offer channel](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672).

### `Fwd`

**Purpose:** connect the interaction on one existing channel to the interaction on another. This is an endpoint-level operation on existing channels. The publication illustrates it with a unit message pending on `c` and a receiver waiting on `d`; see Section 8 for the trace.

**Intended but underspecified:** `Fwd` needs a complete transition rule for channel polarity, pending turns, and continuation state. Polarity is defined in Section 2; Section 9 records the checker's observed assignments. The implementation's turn-like records appear to represent pending communication/exchange state, but `turn` is not used here as a synonym for a communication step. The exact semantics remain open. The publication example and inspected executor do not settle all OrgLang cases; see Section 14 for the canonical open question.

### Summary: compare the three operations

`ExternalCall` and `InternalCall` are the two named-process call forms, with different channel effects and continuation behavior. Record each operation's OrgLang meaning, publication interpretation, and implementation behavior separately. `ExternalCall` starts a named-process incarnation with a fresh provider channel and preserves a continuation for the caller; `InternalCall` starts a named-process incarnation and injects an existing channel into it, transferring provider responsibility with no ordinary continuation for the old incarnation; `Fwd` connects two existing channel interactions, while named-process invocation is described by `ExternalCall` and `InternalCall`.

| Operation | Primary role | Intended control-flow effect | Intended channel effect | Semantic/evidential status | Implementation status |
|---|---|---|---|---|
| `ExternalCall` | Create and invoke a named-process incarnation with a fresh provider channel. | The caller's continuation becomes eligible only after it receives that channel. | Explicit parameter mapping; a fresh provider channel is delivered outward to the caller. | Agreed intended contract; implementation mapping remains open. | Unverified; no executor branch found. |
| `InternalCall` | Create a named-process incarnation by injecting an existing channel inward. | A fresh incarnation takes over; the old incarnation has no ordinary continuation. | The existing channel resource and its client endpoint remain connected; provider responsibility transfers to the new incarnation. | Provisional intended contract; lifecycle and representation open. | Unverified; no complete executor path found. |
| `Fwd` | Connect two existing channel interactions. | No named-process incarnation or named-process continuation transfer is implied. | Relates existing endpoints; no global renaming is implied. | Intended rule open beyond the documented example. | Partial; full symmetric behavior not established. |

Use this table as the quick comparison, and the operation-specific subsections above for the intended transitions and preconditions. Part II gives publication context; Part III records implementation evidence. Those evidence sources are not alternative definitions of the intended behavior.

## Part II. Comparison with the publication

## 8. Comparison with the supplied publication

The supplied publication gives the named-process call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here `p` names the definition, and the rule substitutes actual channel names for the corresponding formal names.

Table 4.2 likewise describes `a ← p b` as a call to named process `p`, which may communicate along channels `a` and `b`. This supports the reading of the construct as named-process invocation and channel substitution. The full OrgLang `ExternalCall` transition, including caller continuation through `ContExp`, is specified in Section 7; the publication rule is comparative context.

Do not conflate named-process call with the separate cut/spawn rule `x ← P ; Q`. The latter has an inline process body `P`, a continuation `Q`, and explicitly allocates a fresh channel shared by the two resulting processes.

### The publication's cut/spawn rule

The publication separately describes cut/spawn as allocating a fresh channel shared by a spawned process and the original process's continuation. The detailed rule is documented in [about-spawn, Section 2.2](../about-spawn/README.md#22-existing-rationale-publication-cutspawn-rule); OrgLang's `Spawn` semantics remain a separate question.

The publication also gives the following forwarding rules. For clarity, the mode parameter `m` is omitted; this discussion focuses on forwarding.

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

The publication's `msg` action is tentatively aligned here with OrgLang's `pub` (publish/send a message), and `srv` with `sub` (subscribe/wait to receive or serve). These mappings are provisional; available evidence has not established synonymy. In the inspected implementation, `PubRec` stores a `ValExp` (publication/message action) and `SubRec` stores a `ContExp` (subscription/service continuation). The `Fwd` executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

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

Section 7 defines the intended channel effects. Here the implementation mapping remains the focus: `CallSpec` exposes `ContExp`, `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH`, but how those fields implement the agreed `ExternalCall` contract is unverified. For `InternalCall` (AST constructor `LinkSpec`), comments in `proc/termdec/core/core.go` suggest that `X` maps to the declaration's `LiabVar` and `Ys[i]` maps to `AssetVars[i]` in declaration order. However, `X` and `Ys` are typed as `identity.ADT`, not `symbol.ADT`; the actual resolution path remains unverified.

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
- **`CallSpec`** — `CommChnlPH`, `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp`: AST/implementation representation associated with the call construct. Its precise mapping to the language-level `ExternalCall` contract remains unverified. It carries a continuation and distinct channel-placeholder fields; how these fields encode the agreed explicit mapping to existing channels remains unverified.
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

The process-level `CheckSpec` and `CheckRec` implementations explicitly handle only `One`, `Tensor`, `Lolli`, `Plus`, and `With`; other expected constructors reach the default panic. The pool-level conversion also includes `Link`, `Up`, and `Down`. This cross-layer difference is an implementation finding, not proof that unresolved forms reach the process checker during ordinary execution. Section 10 records the resulting open question.

One concrete source discrepancy exists in `pool/typeexp/core/tc.go`: the `DownSpec` conversion constructs and returns `UpRec` rather than `DownRec`. Also, the `PlusSpec` conversion composes a value key but does not check/return the `Compose` error in the same way as neighboring branches. These implementation findings require validation with focused tests and should remain separate from the intended type semantics.
## 10. Typing interface

### What type checking does

Before an expression is executed, the implementation checks whether the current channel protocols fit the operation. For example, a send action should only be used when the channel's current protocol permits sending; a close action should only be used when that interaction is ready to finish. These are intuitive explanations; complete formal rules remain to be established.

In the implementation, `proc/compexec/core/core.go` loads the current execution snapshot (a saved view of computation state at that execution point; its relationship to the publication's `configuration` and `environment` is not yet established), gathers relevant process declarations and type definitions, builds the type-checking context, and calls `checkType` before dispatching the expression. Its `LinearVars` map records the channel variables tracked by the checker. The exact invariants of this context remain unverified.

### How to read the correspondence table

The table records which session-type constructor the inspected checker expects for each process operator. “Provider-side” and “client-side” identify the two channel roles described in Section 2. A process as a whole still has one provider channel. A match in this table is evidence about the checker; the full language rule requires separate semantic evidence.

| Process operator | Provider-side expectation | Client-side expectation | Implementation evidence |
|---|---|---|---|
| `Send` | `Tensor` | `Lolli` | Confirmed |
| `Recv` | `Lolli` | `Tensor` | Confirmed |
| `Lab` | `Plus` | `With` | Confirmed |
| `Case` | `With` | `Plus` | Confirmed |
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

- `MsgFromExpSpec` has no branch for the process-expression AST constructor `LinkSpec` (`InternalCall`).
- `MsgToExpSpec` reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. It also reconstructs `LabSpec` without its `ContExp`, although the AST contains that field.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in message-to-AST conversion and in stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.

These source-level discrepancies require focused tests and call-path analysis to establish their runtime impact. The inspected call-related test does not demonstrate a successful transition; the execution findings and limitations are summarized in Section 13.

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

The first fully formalized implementation-level rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. Complete implementation-level reduction rules for `ExternalCall`, `InternalCall`, and resource-management constructs should remain unspecified until the execution paths have been verified and reconciled with the intended contract in Section 7. `Spawn` is deferred to the pool-level analysis. `InternalCall` (AST constructor `LinkSpec`) should be investigated alongside recursive process definitions and named-process invocation, not conflated with `Fwd`.

### Named-process calls: implementation evidence

This subsection records executor-level findings. Adapter discrepancies are listed in Section 12, and Section 14 consolidates the remaining questions.

**Implementation observation:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for the AST constructors `CallSpec` (`ExternalCall`), `SpawnSpec`, `LinkSpec` (`InternalCall`), `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. This describes the current dispatcher, not the language design.

The inspected `ExternalCall`-related `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The process-definition persistence methods inspected so far also appear to be stubs. Thus the repository evidence does not demonstrate a successful transition for the AST `CallSpec` construct associated with `ExternalCall`. See Section 14 for the unresolved argument-mapping question.

**Implementation observation:** `InternalCall` is represented by the process-expression AST constructor `LinkSpec`. Its `X` (provider channel) and `Ys` (client channels) are intended to identify caller-side channels, but the AST types them as `identity.ADT` channel identifiers rather than `symbol.ADT` placeholder names. No complete adapter or executor path was found. The AST `CallSpec` has an explicit `ContExp`; `LinkSpec` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This implementation-level API name alone cannot establish that OrgLang exposes a user-written `Spawn` operation. The repository contains three distinct `Spawn` representations; they should not be treated as one implementation:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode. Instantiating a process body and wiring the fresh channel described by the publication's cut rule are separate steps that this method does not perform.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape and belongs to a separate prototype. It does not establish behavior of the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This provides useful comparison context. Evidence that OrgLang exposes a standalone source-level `Spawn` remains unavailable. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

### Forwarding remains a separate open question

The executor contains a `Fwd` branch. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. The code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads and do not handle `FwdRec` in those switches. It remains unverified whether another part of scheduling and exchange handling covers this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken.

A formal reduction rule should be added after the relevant typing, executor, adapter, and scheduling paths have been checked together.

## 14. Open questions and next tests

The list is ordered by investigation priority.

1. **ExternalCall implementation conformance:** The intended contract is that the caller continuation proceeds only after the provider channel is received. Does the implementation enforce this, and which tests verify that it cannot proceed merely because the new incarnation has started?
2. **ExternalCall / AST mapping:** What is the exact argument syntax for mapping formal parameters to existing, distinct channels, and how does the engine's injection of the separate communication channel into the caller-named placeholder map to `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH`? Where are name resolution, recursion checks, and type checks enforced?
3. **InternalCall representation and lifecycle:** Where should `X` / `Ys` be resolved, and what lifecycle, failure, and scheduling guarantees apply when provider responsibility transfers?
4. **Fwd:** What are the exact transition rules for positive, negative, and neutral polarity, including pending turns and continuation state?
5. **Representation and execution:** Are the conversion asymmetries in Section 12 reachable, and what focused tests establish their impact? Check the relevant adapter, executor, and scheduling paths together.
6. **Type constructors and checker coverage:** Are type-level `Link`, `Up`, and `Down` resolved before the observed checker cases? What tests establish the intended coverage?
7. **Case branch checking:** Does checking one `Case` branch mutate the context used for the next branch? Add a focused test with multiple labels and distinct continuations; verify branch-local context handling.
8. **Linear context:** What are the invariants for `ChnlBS`, provider/client orientation, and updates across operations? Must all `Case` branches preserve equivalent linear contexts?
9. **Publication/subscription state:** What transition semantics do publication, subscription, and exchange-turn records implement?
10. **Process creation:** What is the intended relationship among process-level invocation, pool-level `Spawn`, and the pool model? What is the role of recursion through process definitions?
11. **Other constructors:** What are the contracts of `Acqure`, `Accept`, `Detach`, and `Release`?

## 15. Non-goals

Pool and transaction semantics, resource-allocation policy, fairness, deadlock freedom, and a complete metatheory (such as preservation/progress) are deferred to a separate pass over the pool/transaction implementation.

