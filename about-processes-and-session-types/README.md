# Processes and session types

> **Status: preliminary research draft.** This document describes the intended OrgLang process and session-type model alongside evidence from `orglang/go-engine`.

**Audience:** readers studying OrgLang process expressions and session types, and contributors verifying their representation in `orglang/go-engine`.

**Document structure:** Part I describes the conceptual model and intended operation semantics; Part II presents formal semantics and relation to prior work; Part III records implementation evidence and open questions.

**Contents**
- [Part I — Conceptual model](#part-i-conceptual-model): [core concepts and model invariants](#2-core-concepts), [channel interaction example](#3-a-small-example-following-a-channel), [session types](#6-session-types-for-a-channel), and [named-process calls and incarnation creation](#7-named-process-calls-and-incarnation-creation).
- [Part II — Semantics and relation to prior work](#part-ii-semantics-and-relation-to-prior-work): publication rules and forwarding trace.
- [Part III — Implementation evidence and open questions](#part-iii-implementation-evidence-and-open-questions): [implementation map](#9-implementation-map-process-declarations-and-definitions), [typing](#10-typing-interface), [execution](#11-execution-and-communication), [AST and serialization gaps](#12-ast-and-serialization-gaps), and [open questions](#14-open-questions-and-next-tests).

**Shared terminology:** see the [OrgLang glossary](../GLOSSARY.md).

## Part I. Conceptual model

### 1. Scope and evidence

This research draft describes OrgLang processes and session types, compares the intended model with the supplied publication, and records implementation evidence from `orglang/go-engine`. Pool and transaction semantics are covered separately, with pool-level process creation included where it clarifies the boundary between invocation and spawning. The publication supports claims about its own rules; implementation code supports claims about the inspected implementation.

Three status dimensions must remain separate:

| Dimension | Values | Question it answers |
|---|---|---|
| Claim evidence | **Confirmed**, **Inferred**, **Open** | What does the available evidence establish about this claim? |
| Implementation coverage | **Implemented**, **Partial**, **Absent**, **Unverified** | How much of the relevant behavior has been verified in the implementation? |
| Terminology mapping | **Confirmed**, **Provisional**, **Unresolved** | How strong is the proposed correspondence between OrgLang, publication, and implementation terms? |

For example, a project decision can confirm the intended direction of OrgLang behavior while implementation coverage remains unverified. Identify the decision as the source and state what it explicitly establishes. A claim about a formal language rule needs support from a normative specification or an explicitly adopted language-level contract.

#### Evidence status

Assign status to each individual claim. A term may appear in claims with different evidence statuses.

- **Confirmed** — the claim is directly supported by an appropriate source or by sufficient verified evidence. State what the evidence establishes.
- **Inferred** — the claim is a working interpretation derived from available evidence, but is not directly established.
- **Open** — available evidence does not settle the claim, or relevant verification has not been completed.

Attribute each claim to its source: a publication rule, an OrgLang language rule, or an implementation observation. Confirmation in one category does not transfer automatically to another.


#### Implementation status

Track implementation coverage independently from evidence status.

- **Implemented** — the relevant behavior has been verified in the execution path or by an appropriate test.
- **Partial** — some of the required behavior is implemented, but coverage is incomplete.
- **Absent** — inspection or testing establishes that the relevant behavior is not implemented in the scope examined.
- **Unverified** — implementation coverage has not been established.

An AST constructor establishes syntax support. Runtime support requires evidence from the relevant execution path or tests; inspection of one code path alone cannot establish system-wide absence.

#### Recording claims

For substantial or disputed claims, record the claim, source, evidence status, implementation status (when relevant), and any limitation or next verification step. Use three statement categories: **Language rule** (established for OrgLang), **Implementation observation** (found in the inspected implementation), and **Candidate rule** (awaiting verification or a design decision).

#### Implementation mapping: terminology correspondence

The table records observed or proposed correspondences among OrgLang concepts, publication notation, and implementation identifiers. These mappings relate model concepts to terminology and identifiers in the inspected sources; they do not define language semantics. Mapping status reports correspondence strength, while claim evidence and implementation coverage remain separate.

Use **Confirmed**, **Provisional**, or **Unresolved** for mappings:

- **Confirmed** — the correspondence is supported by sufficient evidence.
- **Provisional** — evidence supports the correspondence, but it still needs verification.
- **Unresolved** — no correspondence is established, or sources appear to conflict. Describe any discrepancy in the mapping table's **Notes** column.

Record mismatches explicitly; treat similarly named concepts as equivalent only when evidence supports that mapping.

### 2. Core concepts

Use the [OrgLang glossary](../GLOSSARY.md) for shared definitions of processes, **term declarations** and **term definitions**, incarnations, channel placeholders, and session types. The abstract channel and endpoint model is defined in [Incarnations and channels, Section 3](../about-incarnations-and-channels/README.md#3-channels-and-endpoints); process-specific provider/client roles and channel cardinality are defined in this document.

Named-process invocation and incarnation creation are specified canonically in [Calls and spawns](../about-calls-and-spawns/README.md). Every incarnation receives a never-reused identity; this is a model-wide identity policy. An environment or substitution associates channel placeholders with the relevant channel resources or endpoints.

For session types, the **provider endpoint** supplies the reference perspective; checking the **client endpoint** accounts for the complementary actions it permits. The request/response example and the evolution of the current session type is illustrated in Section 3.

**Linearity** is the channel usage/ownership discipline. **Model invariant:** channel bindings are non-aliasing: distinct bound channel placeholders refer to distinct channel identities. Consequently, distinct formal channel parameters supplied to a call must map to distinct existing channel identities. The no-alias property is a global assumption of the OrgLang model. `InternalCall` transfers every binding in the environment, so completeness is determined by the full environment. More generally, **normal completion** of a process is permitted only when its current session types permit completion and all linear obligations have been discharged; the inspected type checker rejects a normal-completion attempt while a provider-channel session type remains unfinished; this is an implementation observation, not yet a complete formal language rule. This is distinct from `InternalCall`, whose agreed semantics terminate the old incarnation by transferring its complete channel environment to a replacement incarnation. That transition is not evidence that the transferred protocols are finished. The full linearity invariant and its application across constructs remain open; do not infer them solely from `InternalCall`.


#### Terminology correspondence: OrgLang, publication, and implementation

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
| current session type | Remaining interactions described by the session type | Current session-type value / checker context (`LinearVars`) | Unresolved | Conceptual correspondence only; state-update invariants remain open. |
Record mismatches among OrgLang terminology, publication terminology, and implementation names. Treat these terms as synonyms only when evidence supports the mapping. Intended behavior is described in Section 7; implementation findings and remaining questions are separated in Part III.




### 3. A small example: following a channel

Imagine two processes that communicate over one channel. The **current session type** is the remaining interaction sequence at the channel's current point. A session type is expressed from the provider endpoint's point of view; the client performs the complementary actions. The table describes what each side does as the session type advances.

- **Before the request:**
  - Client: next, send request; then receive response and finish.
  - Provider: next, receive request; then send response and finish.
- **After the request is transferred:**
  - Client: next, receive response; then finish.
  - Provider: next, send response; then finish.
- **After the response is transferred:** both endpoints have only finishing left.
- **Session finished:** both endpoints are finished.

The arrows mean “then” and serve as explanatory notation for the sequence of actions; they are not OrgLang syntax. “Transferred” means both matching send/receive actions have taken place. Starting one side's action alone does not count as transfer. This is a conceptual trace showing how the current session type advances as each side performs its permitted action. A channel is not just a wire carrying arbitrary messages: its session type limits which interaction is allowed next.

**Connection to the implementation vocabulary:** at the process-expression level, the request and response correspond conceptually to complementary `Send`/`Recv` actions, followed by the session type's terminal actions. Section 10 records the observed checker correspondence for `Send`, `Recv`, and `One`. The concrete OrgLang session-type expression is omitted because the exact typing rules and context updates remain to be established. Channel transfer (`Tensor`/`Lolli`) and labelled choice (`Plus`/`With`) are separate session-type forms discussed in Section 6.
### 4. Process declarations and definitions

Recall the recipe analogy from Section 2: a named process is like a recipe, and each run is an incarnation of that process. A **process declaration** describes the recipe's channel interface. A **process definition** supplies the implementation—the expression or process body that carries out the work. The distinction matters because the existence of a declaration alone leaves storage and loading of a usable body unverified. Go-specific names for these concepts are introduced in Part III.

#### Definition, validation, and execution admission

**Agreed project contract:** A program version is admitted to execution only after its statically decidable well-formedness and type obligations have been checked. A failed static obligation is a static error, and the affected version is not admitted.

Keep three categories distinct in operation contracts:

- **Static obligation:** a property decidable from the program version and its available typing/name information at the admission boundary. Examples include arity, positional correspondence, and type compatibility when the relevant definitions and channel identities are statically known.
- **Runtime precondition:** a condition that depends on the current execution state or on a resource allocated during execution, such as whether a fresh incarnation can be created or whether a newly allocated identity is fresh.
- **Transition invariant:** a property that must hold across a successful state transition, such as preserving channel identity and session-type state or preventing observers from seeing a partial transition.

A condition belongs to the static category only when it is decidable at the specified admission boundary. If a target definition is introduced dynamically, its availability can be checked statically for the resulting program version at the point that version is admitted; availability at some later execution point must not be assumed without a corresponding versioning rule. Likewise, allocating a fresh runtime resource is not itself a static check, even if freshness is a required runtime invariant.

OrgLang programs may be further defined at runtime. A new fragment is checked against its expected type when it is defined. That fragment-level check does not replace checking the statically decidable obligations for the whole resulting program version before admission. Each operation's contract identifies its own static obligations, runtime preconditions, and transition invariants; this section defines the shared distinction rather than duplicating every operation-specific list.

This is the intended language-level contract recorded for this research. Whether and where the current implementation enforces it remains a separate implementation question.

### 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Named-process calls:** `ExternalCall` and `InternalCall` are the two named-process call forms specified in [Calls and spawns](../about-calls-and-spawns/README.md).

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The pool-specific `spawn` transaction-type condition is defined in [Pools and transaction types](../about-pools-and-transaction-types/README.md#formal-grammar-and-state-indexed-rules); generic process-incarnation creation is covered by [Calls and spawns](../about-calls-and-spawns/README.md). The full constructor/field inventory is in Part III.

### 6. Session types for a channel

A session type describes the interactions permitted by the session type from the provider endpoint's point of view; the type checker accounts for the client role when checking the other endpoint (Section 2). For the request/response example and the progression of the current session type, see Section 3.

A session type can also describe the transfer of a channel between processes. The sender gives the other process a channel it can use to communicate; the receiver gains access to that channel for the rest of its process. The implementation names the relevant session-type forms `Tensor` and `Lolli`. At a high level, these are the two complementary forms used to describe channel transfer together with the session type that remains after the transfer. Section 9 records the observed polarity assignments and checker coverage; Section 10 describes the typing interface.

The shared paired-interaction matching principle for process channels and pool transaction channels is defined in [Incarnations and channels](../about-incarnations-and-channels/README.md#4-publication-subscription-and-matching). The concrete process-channel constructors, their polarity, and their typing rules remain specific to this document; the pool-specific `Up`/`Down` identity and continuation rules remain in [Pools and transaction types, Section 6.2](../about-pools-and-transaction-types/README.md#62-matched-transitions-continuations-and-channel-identity).

Session types may also allow a choice between labelled alternatives: the implementation uses `Plus` and `With` for the two complementary type forms associated with such choices. `One` represents a completed session type. The implementation contains `Up` and `Down` constructors too, but their process-channel mapping and constructor-specific OrgLang rules are still being investigated; see Section 9 for observed checker coverage and Section 14 for open questions. Pool-channel `Up`/`Down` matching rules are specified separately in [Pools and transaction types, Section 6.2](../about-pools-and-transaction-types/README.md#62-matched-transitions-continuations-and-channel-identity). The name `Link` is overloaded. **Type-level `Link`** is a session-type constructor referring to another type definition. At the process-expression level, the Go AST constructor is `LinkSpec`, which is mapped provisionally to **`InternalCall`** in [Calls and spawns](../about-calls-and-spawns/README.md); implementation mapping details remain in Section 9.

Part III contains the constructor inventory, observed polarity assignments, checker coverage, and open questions.

### 7. Named-process calls and incarnation creation

The canonical language-level contract for `ExternalCall`, `InternalCall`, and process-incarnation creation is defined in [Calls and spawns](../about-calls-and-spawns/README.md). That document owns the call transitions, channel transfer, commit boundaries, and generic incarnation-creation semantics. This specification retains process declarations, definitions, process expressions, session types, and process-channel protocols. Implementation observations about the process AST and execution path remain in Part III.

`Fwd`, which redirects an interaction between existing channels rather than invoking a named process, remains specified below.

#### `Fwd`

**Purpose:** redirect one specific interaction between two existing channels. This is an endpoint-level operation, not named-process invocation.

**Agreed project decision — one-shot forwarding under linearity:** `Fwd` redirects one interaction once and must not duplicate a linear endpoint. The publication's Example 9 illustrates redirection of an existing interaction.

If neither channel has a pending interaction, `Fwd` may initiate the forwarding-side operation on the corresponding endpoint according to forwarding direction and polarity. This initiation may create a pending forwarding record; it does not, by itself, complete the interaction being forwarded or advance that interaction's current session type. Completion still requires the corresponding operation on the other side to match. The exact mapping between polarity, side, and channel state remains open. The model rules out both channels having a pending interaction simultaneously.

**Implementation observation:** the inspected executor has paths for positive and negative polarity, but this does not establish that every path is reachable or correct. Neutral polarity takes an unexpected-polarity error path; a negative-polarity branch has a type-mismatch TODO; and the existing e2e `fwd` test has no result assertion. The pending-turn lookup checks `CommChnlPH`; handling a turn pending only on the other channel is unverified. The implementation therefore does not yet establish the complete transition contract.

The remaining rule must specify the reachable cases for positive and negative polarity when one side has a pending interaction, the treatment of neutral polarity, and the resulting continuation and one-shot consumption. Polarity is defined in Section 2; Section 9 records the checker's observed assignments.

The following is a **review matrix, not a transition rule**. “Channel A” and “channel B” are the two existing channels supplied to `Fwd`; the exact direction mapping remains unresolved.

| Polarity | Pending interaction state | Current status | Required semantic decision or evidence |
|---|---|---|---|
| Positive | Neither A nor B has a pending interaction | **Open** | Specify which endpoint initiates the interaction, which channel is used first, and the resulting continuation. |
| Positive | Only A has a pending interaction | **Open** | Specify how the pending interaction is redirected and how A's pending state is consumed. |
| Positive | Only B has a pending interaction | **Open** | Specify whether the same rule applies symmetrically or whether polarity makes this case invalid. |
| Negative | Neither A nor B has a pending interaction | **Open** | Specify the initiation side and resulting continuation; compare with the positive-polarity case. |
| Negative | Only A has a pending interaction | **Open** | Specify redirection, pending-state consumption, and continuation. |
| Negative | Only B has a pending interaction | **Open** | Specify redirection, pending-state consumption, and continuation; do not infer symmetry without evidence. |
| Neutral | Any state allowed by the model | **Open** | Decide whether neutral polarity is unreachable, invalid, or has defined behavior. The current executor error is implementation evidence, not a language rule. |
| Any | Both A and B have pending interactions | Excluded by current model | Preserve the existing model constraint unless new evidence or an explicit decision revises it. |

For every allowed row, the rule and tests should establish that the interaction is redirected at most once, neither linear endpoint is duplicated, and the resulting continuation agrees with the current session types. Tests should assert observable results and relevant channel/pending-state invariants; merely executing the `Fwd` path is insufficient.


#### Operation index

The intended contracts are specified in the operation-specific subsections above: [`ExternalCall`](../about-calls-and-spawns/README.md#externalcall), [`InternalCall`](../about-calls-and-spawns/README.md#internalcall), and [`Fwd`](#fwd). Part II records publication context; Part III records implementation evidence. Neither evidence section replaces the language-level contracts.

## Part II. Semantics and relation to prior work

### 8. Comparison with the supplied publication

The supplied publication gives the named-process call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here `p` names the definition, and the rule substitutes actual channel names for the corresponding formal names.

Table 4.2 likewise describes `a ← p b` as a call to named process `p`, which may communicate along channels `a` and `b`. This supports the reading of the publication construct as named-process invocation with channel substitution. It does not, by itself, establish OrgLang's complete `ExternalCall` contract or the runtime meaning of `ContExp`; those are project-level intended semantics documented in Section 7, with implementation conformance tracked separately.

Named-process calls are distinct from the cut/spawn rule `x ← P ; Q`, which has an inline process body `P`, a continuation `Q`, and allocates a fresh channel shared by the resulting processes.

#### The publication's cut/spawn rule

The publication separately describes cut/spawn as allocating a fresh channel shared by a spawned process and the original process's continuation. The detailed rule is documented in [Processes and session types, Section 8](#8-comparison-with-the-supplied-publication); OrgLang's `Spawn` semantics remain a separate question.

The publication also gives the following forwarding rules. The mode parameter `m` is omitted in this forwarding discussion.

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

The proposed correspondences between publication terms `msg` / `srv` and OrgLang terms `pub` / `sub` are recorded in the terminology table in Section 2; they remain provisional, not established synonyms. In the inspected implementation, `PubRec` stores a `ValExp` (publication/message action) and `SubRec` stores a `ContExp` (subscription/service continuation). The `Fwd` executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

#### Reading the publication's forwarding example

The publication's Example 9 gives a concrete positive-polarity trace. A sender publishes the unit value `()` on `c`; a receiver is waiting on `d`; and a forwarding process connects the two. The receiver first registers a service waiting on `d`. The forwarding process then produces a forwarding message for the pair `(d, c)`. Matching that forwarding message with the service waiting on `d` redirects the service to wait on `c`; this redirection is distinct from completing the sender's data communication. The sender's pending unit message is received only when it matches the redirected service on `c`, after which the receiver continues as `P`.

The trace therefore contains two matching events: the forwarding message matches the waiting service and redirects it; subsequently, the sender's unit message matches that redirected service and completes the data communication. It keeps occurrences of `d` and `c` distinct except where the redirection transition changes which channel the service uses. The receiver may need another evaluation step to begin listening again after its service has been redirected. The data communication completes only when the sender's unit message matches the redirected service.



## Part III. Implementation evidence and open questions

This part checks how the implementation corresponds to the language model and intended call contracts established in Parts I and II. Read the evidence in sequence: AST and type-checker coverage, representation and serialization, execution paths, then unresolved questions. Interpret each finding within its layer; end-to-end conclusions require evidence across layers.

### 9. Implementation map: process declarations and definitions

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

#### AST and session-type inventory

##### Process-expression AST inventory

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

##### Session-type AST and checker coverage

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
### 10. Typing interface

#### What type checking does

Before an expression is executed, the implementation checks whether the current session types are compatible with the operation. For example, a send action should only be used when the channel's current session type permits sending; a close action should only be used when that interaction is ready to finish. These are intuitive explanations; complete formal rules remain to be established.

In the implementation, `proc/compexec/core/core.go` loads the current execution snapshot (a saved view of computation state at that execution point; its relationship to the publication's `configuration` and `environment` is not yet established), gathers relevant process declarations and type definitions, builds the type-checking context, and calls `checkType` before dispatching the expression. Its `LinearVars` map records the channel variables tracked by the checker. The exact invariants of this context remain unverified.

#### How to read the correspondence table

The table records which session-type constructor the inspected checker expects for each process operator. “Provider-side” and “client-side” identify the process-channel roles defined in [Section 2](#2-core-concepts). A match in this table is evidence about the checker; the full language rule requires separate semantic evidence.
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

### 11. Execution and communication

At a high level, the inspected execution path follows six steps. The names in parentheses are implementation details:

1. Read the saved state of the computation (the execution snapshot).
2. Gather the process declarations and type definitions needed for the current action.
3. Check that the action fits the channel protocols currently in force (`checkType`).
4. Run the matching handler for the action (`takeWith`).
5. Save the resulting state changes and effects.
6. If the action produced a next expression, schedule or continue with it; otherwise return.

This outlines the observed path. The complete rules for blocking, resumption, and channel ownership remain to be established. Constructor-specific execution findings are in Section 13; representation gaps are in Section 12.

Communication may take more than one execution step. If the matching action from the other side is not yet available—for example, the corresponding `Wait` for a `Close`, or a receive for a send—the current action may register that it is waiting and return. **Registering this pending action is not, by itself, a completed interaction or a language-level session-type transition:** the current session type and the participants' continuation eligibility do not advance merely because one side has acted. The language-level interaction takes effect only when the corresponding actions match, as stated by the common paired-interaction principle in Section 6. When the other side becomes available, the inspected implementation updates the exchange state and channel records, and may schedule the continuation. This is an implementation observation, not a complete transition rule or evidence that continuation scheduling occurs at the correct semantic boundary; implementation ordering, ownership, and conformance remain to be verified.

The transition relation and invariants for publication (`pub`), subscription (`sub`), and exchange-turn state remain open; they require tracing the relevant producer and consumer paths together.

### 12. AST and serialization gaps

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

### 13. What the execution path establishes

#### Scope of the evidence

Use the status policy in Section 1 when reading the findings below. End-to-end behavior requires checking typing, adapters, scheduling, and execution together; AST presence or a single handler is not sufficient. The operation-specific gaps are collected in Section 14.

A formal reduction relation should distinguish at least:

- an expression that is ready to execute;
- an expression suspended while waiting for a peer;
- a communication whose peer has arrived;
- the resulting channel/linear-context update;
- continuation scheduling and persistence.

The current evidence supports treating execution as a stateful transition over an execution snapshot plus communication/exchange state. The snapshot may relate to the publication's `configuration` and `environment`, but that mapping remains an inference to verify. It does **not** yet justify importing a generic session-calculus semantics verbatim, nor asserting that each AST constructor has a complete reduction rule.

The first implementation-level transition descriptions should cover constructors whose typing and execution branches have both been checked end-to-end. For `ExternalCall`, `InternalCall`, and resource-management constructs, execution-path coverage and conformance to the intended contract in Section 7 remain unverified. `Spawn` is deferred to the pool-level analysis. Investigate `InternalCall` (AST constructor `LinkSpec`) alongside recursive process definitions and named-process invocation, while keeping its implementation analysis distinct from `Fwd`.

#### Named-process calls: implementation evidence

This subsection records executor-level findings. Adapter discrepancies are listed in Section 12, and Section 14 consolidates the remaining questions.

**Implementation observation:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for the AST constructors `CallSpec` (`ExternalCall`), `SpawnSpec`, `LinkSpec` (`InternalCall`), `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. The type-checking path also has no `CallSpec` or `LinkSpec` case in either `checkProvider` or `checkClient`: after `Take` calls `checkType`, those expressions reach the checker's default panic rather than being accepted or rejected with a typed error. In addition, `LinkSpec.Via()` returns an empty placeholder, while `checkType` first uses `Via()` to look up the active linear channel and panics if it is absent. Thus the inspected path is blocked before the executor transition for both constructors; this is stronger evidence than a missing executor branch alone, but does not establish the intended typing rule. This observation describes the inspected implementation version; language design is documented separately.

The inspected `ExternalCall`-related `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The current process HTTP endpoint `POST /api/v1/procs/:id/steps` converts the supplied SDK step and calls `proc/compexec.API.Take`. That method runs `checkType` before `takeWith` and only then reaches the explicit transaction that calls `ModifyRec`; the checker’s default panic therefore occurs before this service’s execution-record modification step. The handler returns ordinary errors from `Take`, but has no local panic recovery. No conclusion is drawn here about whether outer Echo middleware recovers the panic, so the HTTP status/connection behavior remains unverified. Since `CallSpec` has no checker or executor branch, this inspected process-execution route does not implement `ExternalCall` even if the expression reaches it. Separately, `proc/termdef` service/repository operations are stubs, but the evidence does not establish that this storage path is used by the HTTP step route. The message-adapter and stored-DTO gaps in Section 12 add further obstacles to round-tripping a call. This is an implementation-evidence gap; the intended channel contract is recorded in Section 7.
**Implementation observation:** `InternalCall` is represented by the process-expression AST constructor `LinkSpec`. Its `X` (provider channel) and `Ys` (client channels) are intended to identify caller-side channels. The AST types these fields as `identity.ADT` channel identifiers; placeholder names use `symbol.ADT`. No complete adapter or executor path was found. The AST `CallSpec` has an explicit `ContExp`; `LinkSpec` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This API is an implementation-level operation; OrgLang's user-facing process creation forms are `ExternalCall` and `InternalCall`. The repository contains several separate process-spawning representations:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out. This is an unfinished implementation attempt, not an established language construct.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but does not itself instantiate or attach a process body. The pool executor's separate `Take` route handles pool-level expressions (`Accept`, `Acquire`, `Apply`, `Hire`, `Detach`, `Release`); this does not supply the missing process-level `CallSpec` / `LinkSpec` transitions. Wiring the fresh channel described by the publication's cut rule is also not performed by `Spawn` itself.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape and belongs to a separate prototype. It does not establish behavior of the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This provides useful comparison context but does not define OrgLang behavior. The intended complete process-spawning path and the replacement for the unfinished `SpawnSpec` attempt remain **Open**. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

#### Forwarding remains a separate open question

The inspected executor registers a `PubRec` carrying `FwdRec` when no turn is pending and polarity is positive, and a `SubRec` carrying `FwdRec` when polarity is negative. It also has paths for existing pending-turn records. These observations do not establish that all paths are reachable or correct. Neutral polarity follows an unexpected-polarity error path, one negative-polarity branch has a type-mismatch TODO, and the existing e2e `fwd` test has no result assertion. Complete runtime behavior remains unverified; see Section 14 for the contract questions.

### 14. Open questions and next tests

The list is ordered by investigation priority. [Calls and spawns](../about-calls-and-spawns/README.md) is the canonical statement of intended call semantics; the questions below concern unresolved details or evidence, not a request to restate that contract.

#### Current implementation status at a glance

**Implementation summary:** the inspected repository does not demonstrate a working end-to-end implementation of either named-process call form. Both constructors lack checker and executor branches, and the inspected conversion/DTO paths cannot preserve their full representations. The available `ExternalCall` e2e scenario is disabled/inconclusive. The intended call semantics are recorded in [Calls and spawns](../about-calls-and-spawns/README.md); implementation evidence is detailed in Sections 12–13.

The semantic decisions that should guide implementation are recorded in [Calls and spawns](../about-calls-and-spawns/README.md): `ExternalCall` preserves supplied channel identities and session-type states while transferring their use to the target, and releases the caller continuation only when the fresh provider channel is received; `InternalCall` transfers the complete channel environment to a fresh incarnation and semantically terminates the old one. Model-wide non-aliasing and never-reused incarnation identities are settled assumptions. These decisions do not establish implementation conformance.

The remaining work falls into three different categories and should not be conflated:

- **Implementation blockers:** checker/executor support, lossless AST/message/DTO conversion, and a meaningful end-to-end test path for both call forms.
- **Other semantic questions:** the polarity/pending-turn cases for one-shot `Fwd` remain open.
- **Partly decided lifecycle design:** The language-level `ExternalCall` commit point and the pre-commit behavior when the search-and-negotiation procedure times out are specified here. The shared search-and-negotiation timeout, including manual negotiation, is documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). The timeout's source, who supplies or configures it, and its representation remain open. These are intended semantics, not claims about implementation conformance.

The detailed acceptance tests below are the proposed validation target; they are not claims that tests currently exist or pass. General process/pool failure and post-delivery recovery tests belong to a future fault-tolerance scope.

For process-channel matching, the same suite should include these focused cases:

- **`Send`/`Recv`:** test sender-first and receiver-first arrival. After the first operation, assert a pending action with no completed transfer, session-type advancement, or continuation eligibility. After the matching operation, assert one completed transfer, the shared session-type state effect, and each participant's own continuation behavior.
- **`Close`/`Wait`:** test both arrival orders and the unmatched boundary. After matching, assert that the interaction completes, the provider has no executable continuation, and the client's enclosing continuation becomes eligible only if supplied.
- **`Fwd`:** test forwarding redirection separately from the data transfer it redirects. Assert that matching a forwarding message with a waiting service changes the service's destination but does not complete the sender's data communication; that communication completes only when the sender's message matches the redirected service. Add polarity, one-shot consumption, and linear-endpoint-preservation cases as the constructor-specific rule is formalized.
- **Cross-constructor isolation:** verify that matching on one channel does not advance another channel's current session type or make an unrelated continuation eligible.

These tests must assert observable state and scheduled continuations, not merely successful `Take` calls. The current `fwd` end-to-end test ends with a TODO instead of a result assertion, and the inspected `close`/`wait` scenario also lacks an asserted postcondition.

1. **ExternalCall implementation conformance:** Verify that the caller continuation becomes eligible only after receipt of the provider channel, not merely after the new incarnation starts. The inspected `checkProvider` / `checkClient` checker switches and `takeWith` executor switch have no `CallSpec` (`ExternalCall`) case; the checker reaches its default panic before the executor transition. The process-expression adapter also lacks a `MsgFromExpSpec` branch for `CallSpec`, while `MsgToExpSpec` drops `ContExp` when reconstructing a call. These gaps mean the repository evidence does not establish a complete call path or preservation of the caller continuation. Since `Take` checks types before its execution-record modification transaction, the observed checker panic occurs before that service's explicit `ModifyRec` step; HTTP panic recovery by outer middleware has not been verified. Add focused checker-error, adapter round-trip, and end-to-end conformance tests once the intended typing and transition contract are aligned.
2. **ExternalCall search-and-negotiation timeout conformance:** The language-level commit point and pre-commit search-timeout behavior are specified in Section 7; the timeout policy is documented in [Pools and transaction types, Section 2.1](../about-pools-and-transaction-types/README.md#21-negotiation-and-established-agreement). Remaining work is implementation conformance for the agreed contract. The timeout's source, who supplies or configures it, and its representation remain open.

   - Verify that agreement discovery and candidate negotiation, including escalation to manual intervention, are bounded by the same timeout.
   - Verify timeout expiry before finding a suitable agreement does not create an incarnation or deliver a provider channel, and leaves supplied client-channel identities and session-type states unchanged.
   - Verify that finding a suitable existing agreement or successfully negotiating a new agreement ends the timeout's effect: subsequent engine delay before provider-channel delivery does not trigger this search-and-negotiation timeout.

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

### 15. Non-goals

Pool and transaction semantics, resource-allocation policy, fairness, deadlock freedom, and a complete metatheory (such as preservation/progress) are deferred to a separate pass over the pool/transaction implementation.