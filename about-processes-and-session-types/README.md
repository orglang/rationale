# Processes and session types

> **Status: preliminary research draft.** This document separates intended OrgLang semantics from observations about `orglang/go-engine`. Formal rules should describe language behavior independently of Go structure and field names; implementation notes are included only to track evidence, discrepancies, and questions requiring verification. Syntax present in the AST is not, by itself, evidence that an expression has a complete runtime semantics.

**Audience:** readers who need to understand OrgLang process expressions and session types, and contributors verifying how those concepts are represented in `orglang/go-engine`. The document is a research draft, not a normative language specification.

**How to use this document:**
- Start with Parts I and II for the conceptual model, intended behavior, and comparison with the supplied publication.
- Use Part III when checking those descriptions against the current implementation.
- Read Section 1 for the two independent status axes: semantic/evidential status and implementation status. A semantic claim may be well specified even when the implementation is incomplete or unverified.
- Use Section 14 as the consolidated list of questions still requiring investigation.

**Contents**
- [Part I — Language model](#part-i-language-model): [core concepts and glossary](#2-core-concepts), [protocol example](#3-a-small-example-following-a-channel), [session types](#6-session-types-the-protocol-for-a-channel), and [intended operation semantics](#7-intended-semantics-of-named-process-operations).
- [Part II — Comparison with the publication](#part-ii-comparison-with-the-publication): publication rules and forwarding trace.
- [Part III — Implementation evidence and open questions](#part-iii-implementation-evidence-and-open-questions): [implementation map](#9-implementation-map-process-declarations-and-definitions), [typing](#10-typing-interface), [execution](#11-execution-and-communication), [representation caveats](#12-representation-and-serialization-caveats), and [open questions](#14-open-questions-for-the-next-verification-pass).

## Part I. Language model

## 1. Scope and evidence

This document focuses on processes and session types. Pool and transaction semantics are not formalized here, although pool-level process creation is considered where necessary to understand the boundary between invocation and spawning.

**Status policy.** Keep two axes separate. **Semantic/evidential status** describes what supports a claim: **Specified** means stated directly in the relevant language source or publication; **Observed** means directly visible in inspected source or comments; **Inferred** means a working interpretation derived from evidence but not directly specified; **Open** means the available evidence does not settle the question. **Implementation status** describes implementation coverage independently: **Implemented**, **Partial**, **Not implemented**, or **Unverified**. Use **Intended behavior** in prose for a proposed or target language-level contract, not as an evidence label. Do not infer implementation completeness from a semantic status, or semantic correctness from implementation evidence.

## 2. Core concepts

OrgLang processes communicate through **channels**. A channel is the shared communication resource connecting two roles: the **provider** offers a service, and the **client** uses it. An **endpoint** is one participant's role-specific side of that channel—the provider endpoint or the client endpoint. In this document, “provider channel” and “client channel” describe a channel from the relevant process's role; they do not imply two separate channels. Each process has one provider channel of its own and may use other channels as a client.

**Process** is the general umbrella term in this document; its precise referent follows context. A **named process** is the process identified by a name. A **process declaration** describes its interface, while a **process definition** supplies its behavior. Each start creates a concrete running copy called a **process incarnation**. These are related concepts, not interchangeable terms. A **channel placeholder** is a name in an expression or process interface that is intended to stand for a channel. It is a syntactic name, not the channel resource or endpoint itself; an environment or substitution must associate it with the relevant channel. The implementation may represent these layers with different Go types, and the mapping must be verified rather than inferred from field names alone.

A **session type** describes the allowed protocol from an endpoint's point of view; the complementary endpoint may describe complementary actions. A **residual session type** is the remaining part of that protocol after prior interaction steps. The request/response example and the meaning of a **residual session type** are introduced in Section 3.

**Linearity** is a term used for a usage/ownership discipline in the channel model. The exact object to which linearity applies and its formal invariant must be grounded in the language rules or publication; do not treat a particular formulation as established solely from the `Link` operation.

### Quick glossary

| Term | Meaning in this document |
|---|---|
| Channel | The shared communication resource used by a provider and a client. |
| Endpoint | One role-specific side of a channel: provider endpoint or client endpoint. |
| Provider / client | Roles on the same channel: offering a service / using it. |
| Process | General umbrella term; interpret in context rather than equating it only with a name or a running instance. |
| Named process | A process referred to by name. |
| Process declaration | The process interface, including its provider-role and client-role channel placeholders. |
| Process definition | The body or expression specifying process behavior. |
| Process incarnation | One running instance of a process. |
| Channel placeholder | A syntactic name intended to be associated with a channel; not the channel resource itself. |
| Session type | The protocol describing which interaction is allowed on a channel. |
| Residual session type | The part of that protocol still to be performed at the current point. |
| Linearity | A usage/ownership discipline; the precise invariant and its object require confirmation from the formal rules. |
| Polarity | An implementation-level positive/negative/neutral classification used by the type checker; not a complete explanation of operational behavior. |
| Snapshot | An implementation concept that may relate to the publication's `configuration` and `environment`; the exact mapping is an open hypothesis, not an established equivalence. |
| Turn | Do not treat as a general language-level concept unless a distinct meaning is established. The implementation uses turn-like records for pending communication/exchange state; their precise semantics remain open. |

### Terminology correspondence: OrgLang, publication, and implementation

| Concept | OrgLang language-level term | Publication notation / term | Implementation name(s) | Notes |
|---|---|---|---|---|
| Channel roles | provider / client | provider / client roles in the process interface | `LiabVar` / `AssetVars` in `DecSpec`; `X` / `Ys` in `Link` | `LiabVar` is the declaration's provider-role name; `AssetVars` are client-role names. For process-expression `Link`, the intended mapping is **`providerChannel` (`X`)** to `LiabVar` and **`clientChannels` (`Ys`)** to `AssetVars` in declaration order. `LinkSpec.X` / `Ys` are typed as `identity.ADT`, unlike the `symbol.ADT` placeholder representation; runtime resolution is unverified. |
| Named-process invocation | `Call` | `a ← p b` and `proc(a ← p b) → proc(P[a/x, b/y])` | `CallSpec`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, `NewChnlPH` | The publication supports invocation and substitution; OrgLang continuation and argument mapping remain open. The inspected executor has no `Call` branch. |
| Provider handoff | `Link` | No equivalent established in the inspected excerpt | `LinkSpec`, `ProcTermQN`, `X`, `Ys` | Transfers provider responsibility for an existing channel; the old incarnation has no ordinary continuation. No complete adapter/executor path was found. |
| Forwarded message action | `pub` (publish/send) | `msg` | `PubRec`, `ValExp` | `msg` is the send/message side; implementation stores the action in `ValExp`. |
| Forwarded service action | `sub` (subscribe/wait/serve) | `srv` | `SubRec`, `ContExp` | `srv` is the service/waiting side; implementation stores the continuation in `ContExp`. |
| Protocol remaining at a point | residual session type | Remaining protocol after an interaction step | Current session-type value / checker context (`LinearVars`) | Defined in Section 3; state-update invariants remain open. |
| Polarity | positive / negative / neutral | `+` / `−` in the forwarding rules | Type-checker assignments in `proc/typeexp/core/core.go` | Positive: `One`, `Tensor`, `Plus`; negative: `Lolli`, `With`; neutral: `Up`, `Down`, type-level `Link`. |

The table gives the main terminology mapping. Intended behavior is described in Section 7; implementation findings and remaining questions are separated in Part III.



## 3. A small example: following a channel

Imagine two processes that communicate over one channel. The **residual session type** is the part of an endpoint's protocol still to be performed at the current point. The table tracks the protocol from **each endpoint's point of view**. The client and provider have complementary actions, so their residual session types are not necessarily written as the same sequence.

- **Before the request:**
  - Client: next, send request; then receive response and finish.
  - Provider: next, receive request; then send response and finish.
- **After the request is transferred:**
  - Client: next, receive response; then finish.
  - Provider: next, send response; then finish.
- **After the response is transferred:** both endpoints have only finishing left.
- **Protocol finished:** both endpoints are finished.

The arrows mean “then”; they are explanatory notation, not literal OrgLang syntax. “Transferred” means the matching send/receive actions have both taken place, not merely that one side has started its action. This is a conceptual trace showing how each endpoint's residual type advances according to its own action. A channel is not just a wire carrying arbitrary messages: its session type limits which interaction is allowed next.

**Connection to the implementation vocabulary:** at the process-expression level, the request and response correspond conceptually to complementary `Send`/`Recv` actions, followed by the protocol's finishing actions. Section 10 records the observed checker correspondence for `Send`, `Recv`, and `One`; it is not a complete typing derivation. This example deliberately does not assign a concrete OrgLang session-type expression to the whole protocol, because the exact typing rules and context updates are not yet fully established. It also does not illustrate channel transfer (`Tensor`/`Lolli`) or labelled choice (`Plus`/`With`); those are separate protocol forms discussed in Section 6.

## 4. Process declarations and definitions

Recall the recipe analogy from Section 2: a named process is like a recipe, and each run is an incarnation of that process. A **process declaration** describes the recipe's interface—the channels it expects, including one provider channel and any channels it uses as a client. A **process definition** supplies the implementation—the expression or process body that carries out the work. The distinction matters because a declaration can exist even when the repository does not establish that a usable body is stored or can be loaded. Go-specific names for these concepts are introduced in Part III.

## 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Process control:** `Call` invokes a named process while the caller has a continuation; process-expression `Link` hands provider responsibility for an existing channel to a new process incarnation. Intended transitions are described in Section 7.

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The full constructor/field inventory is in Part III.

## 6. Session types: the protocol for a channel

A session type describes the allowed protocol from one endpoint's point of view (Section 2). For the request/response example and residual session types, see Section 3.

A protocol can also pass a channel between processes. The sender gives the other process a channel it can use to communicate; the receiver gains access to that channel for the rest of its process. The implementation names the relevant session-type forms `Tensor` and `Lolli`. At a high level, these are the two complementary forms used to describe channel transfer together with the protocol that remains after the transfer. The names alone do not tell the reader which endpoint performs which action: Section 9 records the observed polarity assignments and checker coverage, while Section 10 describes the typing interface. The exact direction mapping remains deliberately unstated here.

Protocols may also allow a choice between labelled alternatives: the implementation uses `Plus` and `With` for the two complementary type forms associated with such choices. `One` represents a finished protocol. The implementation contains `Up` and `Down` too, but their meaning in OrgLang is still being investigated; see Section 9 for observed checker coverage and Section 14 for open questions. The name `Link` is overloaded: **type-level `Link`** is a session-type constructor referring to another type definition; **process-expression `Link`** is the process operation that hands off provider responsibility for a channel (Section 7).

This introduction explains why these forms are useful; it is not a complete theory of session types. Part III contains the constructor inventory, observed polarity assignments, checker coverage, and open questions.

## 7. Intended semantics of named-process operations

**This is the canonical statement of the intended language-level behavior.** The comparison with the publication and the implementation notes below provide evidence and caveats; they should not be read as alternative definitions of these operations. Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

This section distinguishes two kinds of uncertainty:

- **Intended but underspecified:** the broad behavior is stated here, but its precise rule, conditions, or edge cases still need to be written down and checked.
- **Design question:** the available evidence does not settle which behavior or mechanism OrgLang should choose. This needs an explicit design decision, not just a more precise description.


### `Call`

**Before:** the caller is executing a `Call` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Intended transition:** resolve the named process and the caller-supplied channel placeholders, then start a fresh incarnation of the named process with the channels required by its declaration.

**After:** the new incarnation can execute independently. The original caller remains active and continues with `ContExp`. Existing channels passed as arguments retain their identity.

**Status:** the high-level control-flow contract is intended, but channel wiring remains underspecified. The unresolved argument mapping and the role of `NewChnlPH` are listed in Section 14. This description does not assume that `Call` is implemented using `Spawn`.

### `Link`

**Before:** the invoking process provides a service on an existing channel, called **`providerChannel`** here (AST field `X`). The target process also receives a list of client channels, called **`clientChannels`** here (AST field `Ys`). These are semantic labels for the explanation; they do not confirm how the runtime resolves the fields.

**Preconditions:** the target process definition is available and a fresh incarnation can be created. The channel supplied by `X` must have the same **current residual session type** as the target process's provider channel—not merely the same initial declared type. In plain terms, both sides must agree on what is supposed to happen next in the conversation. If the existing channel has already passed the request step, the new process must be ready for the response step, not for a new request.

**Intended transition:** start a fresh incarnation of the named process, passing `providerChannel` as its provider channel and `clientChannels` as its client channels, in declaration order. Transfer provider-side responsibility for the existing `providerChannel` to the new incarnation.

**After:** `providerChannel` and its existing client connection remain unchanged; the new incarnation provides that same channel. Control transfers to the new incarnation, and the old incarnation has no ordinary continuation.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` provides channel `c`, and the client has already sent a request. The protocol remaining on `c` is now “send response, then finish.” `Old` performs `Link` to process `New`, passing `c`. `New` takes over the same provider endpoint and continues with “send response, then finish”; it must not restart by waiting for a new request. `Old` does not continue after the handoff. This resembles a tail call in control flow: responsibility is handed off rather than returning to the old process. The analogy is limited—`Link` also preserves the existing channel and its current protocol state.

**Status:** the high-level handoff contract is intended, but lifecycle guarantees are not established by the inspected evidence. See Section 14 for the unresolved lifecycle and representation questions. This contract does not assume that `Link` is implemented using `Spawn`.

### `Fwd`

**Purpose:** connect the interaction on one existing channel to the interaction on another. This is an endpoint-level connection, not a named-process invocation. The publication illustrates it with a unit message pending on `c` and a receiver waiting on `d`; see Section 8 for the trace.

**Intended but underspecified:** `Fwd` needs a complete transition rule for channel polarity, pending turns, and continuation state. Polarity is defined in Section 2; Section 9 records the checker's observed assignments. The implementation's turn-like records appear to represent pending communication/exchange state, but `turn` is not used here as a synonym for a communication step. The exact semantics remain open. The publication example and inspected executor do not settle all OrgLang cases; see Section 14 for the canonical open question.

### Summary: compare the three operations

These operations are not interchangeable. `Call` starts a named-process incarnation and preserves a continuation for the caller; `Link` starts a named-process incarnation that takes over provider responsibility, with no ordinary continuation for the old incarnation; `Fwd` connects two existing channel interactions and does not itself imply a named-process invocation.

| Operation | Primary role | Intended process-control effect | Intended channel effect | Semantic/evidential status | Implementation status |
|---|---|---|---|---|
| `Call` | Invoke a named process. | A fresh incarnation starts; the caller continues with `ContExp`. | Existing argument channels retain their identity. Allocation and mapping involving `NewChnlPH` remain unresolved. | Inferred target contract; details open. | Unverified; no executor branch found in the inspected dispatcher. |
| `Link` | Hand off provider responsibility. | A fresh incarnation takes over; the old incarnation has no ordinary continuation. | The existing `providerChannel` (`X`) and its client connection stay the same. | Inferred target contract; lifecycle and representation open. | Unverified; no complete executor path found. |
| `Fwd` | Connect two existing channel interactions. | No named-process incarnation or named-process continuation transfer is implied. | Relates existing endpoints; no global renaming is implied. | Intended rule open beyond the documented example. | Partial; full symmetric behavior not established. |

Use this table as the quick comparison, and the operation-specific subsections above for the intended transitions and preconditions. Part II gives publication context; Part III records implementation evidence. Those evidence sources are not alternative definitions of the intended behavior.

## Part II. Comparison with the publication

## 8. Comparison with the supplied publication

The supplied publication gives the named-process call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here `p` names the definition, and the rule substitutes actual channel names for the corresponding formal names.

Table 4.2 likewise describes `a ← p b` as a call to named process `p`, which may communicate along channels `a` and `b`. This supports the reading of the construct as named-process invocation and channel substitution. **It does not specify OrgLang's full `Call` transition or establish that the caller continues through OrgLang's `ContExp`.** For the intended OrgLang contract, use Section 7; keep the publication's rule as supporting context, not proof of the whole contract.

Do not conflate named-process call with the separate cut/spawn rule `x ← P ; Q`. The latter has an inline process body `P`, a continuation `Q`, and explicitly allocates a fresh channel shared by the two resulting processes.

### The publication's cut rule: allocate a channel and spawn

The publication gives this rule:

    proc(x ← P ; Q) 7→ proc([a/x]P), proc([a/x]Q) (a fresh)
    cut: allocate channel & spawn

Table 4.2 explains the term `x ← P ; Q` in plain language: allocate a new channel `a`, spawn a process running `P[a/x]`, and continue the original process as `Q[a/x]`. The two processes may communicate using the same fresh channel `a`.

So `P` is the body of the process being spawned, while `Q` is the continuation of the original process. The rule combines channel allocation and process spawning; it does not describe two arbitrary processes or two equivalent continuations.

This clarifies the publication's intended meaning, but it does not yet tell us exactly how OrgLang's `SpawnSpec` represents `P` and `Q`, how the channel is represented in OrgLang, or how process-pool lifecycle and scheduling work. Those questions remain open, especially because the inspected implementation attempts are incomplete. Treat this as the publication's semantics, not yet as a complete OrgLang `Spawn` semantics.

The publication also gives the following forwarding rules. The mode parameter `m` is omitted here to keep the discussion focused on forwarding rather than channel modes:

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

In OrgLang, the publication's `msg` action corresponds to `pub` (publish/send a message), and `srv` corresponds to `sub` (subscribe/wait to receive or serve). In the inspected implementation, `PubRec` stores a `ValExp` (publication/message action) and `SubRec` stores a `ContExp` (subscription/service continuation). The `Fwd` executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

### Reading the publication's forwarding example

The publication's Example 9 gives a concrete positive-polarity trace. A sender publishes the unit value `()` on `c`; a receiver is waiting on `d`; and a forwarding process connects the two. The receiver first becomes a service waiting on `d`. The forwarding process then produces a forwarding message for the pair `(d, c)`. When that forwarding message meets the service waiting on `d`, the service is redirected to wait on `c`; the sender's pending unit message can then be received, and the receiver continues as `P`.

The important point is that forwarding is shown as an interaction between a forwarding message and a waiting service, not as a global renaming of every occurrence of `d` to `c`. The trace also shows that the receiver may need another evaluation step to begin listening again after its service has been redirected.



## Part III. Implementation evidence and open questions

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

In Section 7, `ContExp` names the continuation expression for `Call`; `NewChnlPH` names a channel placeholder whose allocation or supply is not yet established. For process-expression `Link`, `X` is intended to identify the existing provider channel being handed off, and `Ys` the client channels passed to the new process. However, `LinkSpec.X` and `LinkSpec.Ys` are typed as `identity.ADT`, not `symbol.ADT`; the AST therefore does not represent them using the same type as the channel placeholders elsewhere. Here “placeholder” describes their intended language-level role, not a confirmed implementation representation. The actual resolution path remains unverified.

Comments in `proc/termdec/core/core.go` support these readings. For process-expression `Link`, the intended mapping is `providerChannel` (`X`) → `LiabVar` and `clientChannels[i]` (`Ys[i]`) → `AssetVars[i]` in declaration order. These are implementation field names; the language-level description uses provider and client roles.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/`Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. In particular, `LinkSpec.X` and `LinkSpec.Ys` are `identity.ADT` values, not channel placeholders (`symbol.ADT`). In the intended language-level semantics, they denote caller-side channel placeholders; the Go field types are an implementation discrepancy, not the semantic definition:

- `TermQN`: qualified name associated with a declaration;
- `ProcQN`: qualified name associated with a definition;
- `ProcTermQN`: name referenced by call/spawn expression constructors;
- expression identity / `valkey`: a candidate identifier for an expression incarnation, whose exact lifecycle remains to be confirmed.

Do not assume these identifiers are interchangeable.

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
- **`CallSpec`** — `CommChnlPH`, `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp`: candidate named-process call representation. Unlike the publication form `a ← p b₁ … bₙ`, it carries a continuation and distinct channel placeholders whose roles remain unsettled.
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

The polarity assignments above are **Observed** in `proc/typeexp/core/core.go`. They classify session types as positive, negative, or neutral; they do not define all operational cases.

At the AST level, process `Plus`/`With` choices are represented as label-indexed alternatives. The exact normalization and lookup rules for type references, and how `Up`/`Down` are unfolded, remain to be confirmed.

The current process-level `CheckSpec` and `CheckRec` implementations explicitly handle only `One`, `Tensor`, `Lolli`, `Plus`, and `With`; any other expected constructor reaches the default panic. In contrast, the pool-level type-expression conversion includes `Link`, `Up`, and `Down` cases. This is evidence that the repository has multiple layers with different constructor coverage, not proof that the process checker is reached with unresolved `Link`/`Up`/`Down` in ordinary execution.

One concrete source discrepancy exists in `pool/typeexp/core/tc.go`: the `DownSpec` conversion constructs and returns `UpRec` rather than `DownRec`. Also, the `PlusSpec` conversion composes a value key but does not check/return the `Compose` error in the same way as neighboring branches. These are implementation findings only; they should be validated with focused tests and should not be used to define the intended type semantics.
## 10. Typing interface

### What type checking does

Before an expression is executed, the implementation checks whether the current channel protocols fit the operation. For example, a send action should only be used when the channel's current protocol permits sending; a close action should only be used when that interaction is ready to finish. These are intuitive explanations, not complete formal rules.

In the implementation, `proc/compexec/core/core.go` loads the current execution snapshot (a saved view of computation state at that execution point; its relationship to the publication's `configuration` and `environment` is not yet established), gathers relevant process declarations and type definitions, builds the type-checking context, and calls `checkType` before dispatching the expression. Its `LinearVars` map records the channel variables tracked by the checker. The exact invariants of this context still need verification.

### How to read the correspondence table

The table records which session-type constructor the inspected checker expects for each process operator. “Provider-side” and “client-side” identify the two channel roles described in Section 2; they do not mean that the whole process has two provider channels. A match in this table is evidence about the checker, not a complete language rule.

| Process operator | Provider-side expectation | Client-side expectation | Implementation evidence |
|---|---|---|---|
| `Send` | `Tensor` | `Lolli` | Observed |
| `Recv` | `Lolli` | `Tensor` | Observed |
| `Lab` | `Plus` | `With` | Observed |
| `Case` | `With` | `Plus` | Observed |
| `Close` / `Wait` | `One` on the corresponding endpoint side | `One` on the corresponding endpoint side | Unverified |
| `Fwd` | compatibility/polarity checks exist | full symmetric behavior not established | Partial |

This table records checker observations, not complete typing rules. Exact side conditions, context splitting, substitution, and freshness conditions remain outside its scope.

The inspected checker explicitly handles `One`, `Tensor`, `Lolli`, `Plus`, and `With`. Its default branch appears to panic for `Link`, `Up`, and `Down`, which means those forms are not handled at that point in the code. Whether normal execution resolves or unfolds these constructors before this code is reached is an open question, not yet a confirmed runtime bug.

## 11. Execution and communication

At a high level, the inspected execution path follows six steps. The names in parentheses are implementation details:

1. Read the saved state of the computation (the execution snapshot).
2. Gather the process declarations and type definitions needed for the current action.
3. Check that the action fits the channel protocols currently in force (`checkType`).
4. Run the matching handler for the action (`takeWith`).
5. Save the resulting state changes and effects.
6. If the action produced a next expression, schedule or continue with it; otherwise return.

This is an outline of the observed path, not a complete definition of when a process blocks, resumes, or owns a channel. The execution inventory is in Section 13; conversion asymmetries are listed in Section 12.

Communication may take more than one execution step. If the matching action from the other side is not yet available—for example, the corresponding `Wait` for a `Close`, or a receive for a send—the current action may register that it is waiting and return. When the other side becomes available, the implementation updates the exchange state and channel records, and may schedule the continuation. The precise ordering and ownership rules are still open.

The exact transition relation, message ownership, and invariants for subscriptions, publications, and exchange turns still need to be formalized from all producer/consumer call paths. Here, a publication (`pub`) is the send/message side and a subscription (`sub`) is the waiting/service side in the terminology used by this implementation; the exact state invariants remain open.

## 12. Representation and serialization caveats

The adapter in `proc/termexp/adapter/tc.go` translates between AST, message, and stored representations. This section lists conversion discrepancies; Section 13 separately records execution support.

- `MsgFromExpSpec` has no `Link` branch.
- `MsgToExpSpec` reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. It also reconstructs `LabSpec` without its `ContExp`, although the AST contains that field.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in message-to-AST conversion and in stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.

These are source-level discrepancies to validate with focused tests and call-path analysis. Their observable runtime impact is not established by this document. The current call example also does not demonstrate a successful transition; the evidence and its limitations are summarized in Section 13.

## 13. Operational semantics: conservative scope

### Evidence limits

Apply the evidence policy in Section 1 throughout: AST presence alone does not establish runtime support, publication rules do not automatically define OrgLang semantics, and a single code path does not establish end-to-end behavior without checking typing, adapters, scheduling, and execution together. The operation-specific questions are listed in Section 14.

A formal reduction relation should distinguish at least:

- an expression that is ready to execute;
- an expression suspended while waiting for a peer;
- a communication whose peer has arrived;
- the resulting channel/linear-context update;
- continuation scheduling and persistence.

The current evidence supports treating execution as a stateful transition over an execution snapshot plus communication/exchange state. The snapshot may relate to the publication's `configuration` and `environment`, but that mapping remains an inference to verify. It does **not** yet justify importing a generic session-calculus semantics verbatim, nor asserting that each AST constructor has a complete reduction rule.

The first fully formalized implementation-level rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. A complete implementation-level reduction rule for `Call` and resource-management constructs should remain unspecified until the execution paths have been verified and reconciled with the intended contract in Section 7. `Spawn` is deferred to the pool-level analysis. `Link` should be investigated alongside recursive process definitions/calls, not conflated with `Fwd`.

### Named-process operations: implementation evidence

This subsection records implementation findings for `Call`, `Link`, and process creation. Section 12 lists conversion discrepancies; Section 14 is the canonical list of unresolved questions.

**Observed:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for `Call`, `Spawn`, `Link`, `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. This describes the current dispatcher, not the language design.

The inspected `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The process-definition persistence methods inspected so far also appear to be stubs. Thus the repository evidence does not demonstrate a successful `Call` transition. See Section 14 for the unresolved argument-mapping question.

**Observed:** for process-expression `Link`, `X` (`providerChannel`) and `Ys` (`clientChannels`) are intended to identify caller-side channels, but the AST types them as `identity.ADT` channel identifiers rather than `symbol.ADT` placeholder names. No complete adapter or executor path was found. `Call` has an explicit `ContExp`; `Link` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This implementation-level API name is not evidence that OrgLang exposes a user-written `Spawn` operation. The repository contains three distinct `Spawn` representations; they should not be treated as one implementation:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but does not itself instantiate a process body or wire the fresh channel described by the publication's cut rule.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape, but is a separate prototype, not evidence for the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This is useful comparison context, not evidence that OrgLang exposes a standalone source-level `Spawn`. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

### Forwarding remains a separate open question

The executor contains a `Fwd` branch. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. The code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads and do not handle `FwdRec` in those switches. It remains unverified whether another part of scheduling and exchange handling covers this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken.

A formal reduction rule should be added after the relevant typing, executor, adapter, and scheduling paths have been checked together.

## 14. Open questions for the next verification pass

1. **Call:** What is the role and ordering of additional channel arguments, and how do they map to formal channel parameters? What is the role of `NewChnlPH`—is its channel allocated, supplied by the caller, or injected by the runtime? Where are name resolution, recursion checks, and type checks enforced?
2. **Link:** Where should `X` / `Ys` be resolved, and what lifecycle, failure, and scheduling guarantees apply when provider responsibility transfers?
3. **Fwd:** What are the exact transition rules for positive, negative, and neutral polarity, including pending turns and continuation state?
4. **Process creation:** What is the intended relationship among process-level invocation, pool-level `Spawn`, and the pool model? What is the role of recursion through process definitions?
5. **Type constructors:** Are type-level `Link`, `Up`, and `Down` resolved before the observed checker cases?
6. **Other constructors:** What are the contracts of `Acqure`, `Accept`, `Detach`, and `Release`?
7. **Linear context:** What are the invariants for `ChnlBS`, provider/client orientation, and updates across operations? Must all `Case` branches preserve equivalent linear contexts?
8. **Representation and execution:** Are the conversion asymmetries in Section 12 reachable, and what tests establish their impact?
9. **Publication/subscription state:** What transition semantics do publication, subscription, and exchange-turn records implement?

## 15. Non-goals

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation.

