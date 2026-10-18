# Processes and session types

> **Status: preliminary research draft.** This document separates intended OrgLang semantics from observations about `orglang/go-engine`. Formal rules should describe language behavior independently of Go structure and field names; implementation notes are included only to track evidence, discrepancies, and questions requiring verification. Syntax present in the AST is not, by itself, evidence that an expression has a complete runtime semantics.

**Audience:** readers who need to understand OrgLang process expressions and session types, and contributors verifying how those concepts are represented in `orglang/go-engine`. The document is a research draft, not a normative language specification.

**How to use this document:**
- Start with Parts I and II for the conceptual model, intended behavior, and comparison with the supplied publication.
- Use Part III when checking those descriptions against the current implementation.
- Read Section 1 for the independent evidence and implementation status axes. A claim may be confirmed by a source even when the implementation is incomplete or unverified.
- Use Section 14 as the consolidated list of questions still requiring investigation.

**Contents**
- [Part I — Language model](#part-i-language-model): [core concepts and glossary](#2-core-concepts), [protocol example](#3-a-small-example-following-a-channel), [session types](#6-session-types-the-protocol-for-a-channel), and [intended operation semantics](#7-intended-semantics-of-named-process-operations).
- [Part II — Comparison with the publication](#part-ii-comparison-with-the-publication): publication rules and forwarding trace.
- [Part III — Implementation evidence and open questions](#part-iii-implementation-evidence-and-open-questions): [implementation map](#9-implementation-map-process-declarations-and-definitions), [typing](#10-typing-interface), [execution](#11-execution-and-communication), [representation caveats](#12-representation-and-serialization-caveats), and [open questions](#14-open-questions-for-the-next-verification-pass).

## Part I. Language model

## 1. Scope and evidence

This document describes OrgLang processes and session types, compares the intended language model with the supplied publication, and records evidence from `orglang/go-engine`.

Pool and transaction semantics are not formalized here, although pool-level process creation is considered where necessary to understand the boundary between invocation and spawning.

It is a research draft, not a normative language specification. The publication is evidence for the rules it states, but is not automatically an authoritative specification of OrgLang. Implementation behavior is evidence about the implementation, not proof of a language-level rule.

### Evidence status

Assign a status to an individual claim, not to a term as a whole.

- **Confirmed** — the claim is directly supported by an appropriate source or by sufficient verified evidence. State what the evidence establishes.
- **Inferred** — the claim is a working interpretation derived from available evidence, but is not directly established.
- **Open** — available evidence does not settle the claim, or relevant verification has not been completed.

Use the source to distinguish a language rule, a publication rule, and an implementation observation. A claim confirmed by one source is not automatically confirmed for another.

### Implementation status

Track implementation coverage independently from evidence status.

- **Implemented** — the relevant behavior has been verified in the execution path or by an appropriate test.
- **Partial** — some of the required behavior is implemented, but coverage is incomplete.
- **Absent** — inspection or testing establishes that the relevant behavior is not implemented in the scope examined.
- **Unverified** — implementation coverage has not been established.

Finding an AST constructor does not establish runtime support. Failing to find a handler in one code path does not, by itself, establish that the behavior is absent throughout the system.

### Recording claims

For substantial or disputed claims, record:

| Field | Purpose |
|---|---|
| Claim | The specific statement being evaluated. |
| Source | The relevant language material, publication, code, or test. |
| Evidence status | Confirmed, Inferred, or Open. |
| Implementation status | Implemented, Partial, Absent, or Unverified, when relevant. |
| Notes | Limitations, discrepancies, and the next verification step. |

Keep simple glossary entries lightweight. Use the full record for semantic rules, implementation claims, and discrepancies between sources.

Distinguish three kinds of statement in prose:

- **Language rule** — a rule established for OrgLang.
- **Implementation observation** — behavior or structure found in the inspected implementation.
- **Candidate rule** — a proposed interpretation awaiting verification or a design decision.

Do not promote a candidate rule to a language rule merely because it is described in detail or reflected in the current code. Record unresolved questions and the evidence needed to resolve them.

### Terminology mappings

The correspondence between OrgLang, the publication, and implementation identifiers is tracked separately in the terminology table. Its mapping status describes the correspondence, not the certainty of an individual claim or the completeness of the implementation.

Use **Confirmed**, **Provisional**, or **Unresolved** for mappings. Preserve mismatches rather than silently treating similarly named concepts as equivalent.

## 2. Core concepts

OrgLang processes communicate through **channels**. A channel is the shared communication resource connecting two roles: the **provider** offers a service, and the **client** uses it. An **endpoint** is one participant's role-specific side of that channel: the **provider endpoint** belongs to the process offering the service, and the **client endpoint** belongs to the process using it. A **provider channel** is a channel viewed from the process that provides on it; a **client channel** is a channel viewed from the process that uses it. These names describe a channel's role relative to a particular process, not permanent kinds of channel: the same channel is the provider channel for one process and a client channel for the other. Thus, *channel* names the shared resource, while *endpoint* names one participant's side of it. Each process has one provider channel of its own and may use other channels as a client. The language-level concept **Call** is the umbrella term for two related named-process operations: **`ExternalCall`** and **`InternalCall`**. Both create a fresh process incarnation; they differ in the direction in which a channel is transferred relative to that new incarnation.

**Process** is the general umbrella term in this document; its precise referent follows context. A **named process** is the process identified by a name. A **process declaration** describes its interface, while a **process definition** supplies its behavior. Each start creates a concrete running copy called a **process incarnation**. These are related concepts, not interchangeable terms. A **channel placeholder** is a name in an expression or process interface that is intended to stand for a channel. It is a syntactic name, not the channel resource or endpoint itself; an environment or substitution must associate it with the relevant channel. The implementation may represent these layers with different Go types, and the mapping must be verified rather than inferred from field names alone.

A **session type** describes the allowed protocol from the provider endpoint's point of view. When checking the client endpoint, the type checker accounts for the client role and the complementary actions it permits. A **residual session type** is the remaining part of that protocol after prior interaction steps. The request/response example and the meaning of a **residual session type** are introduced in Section 3.

**Linearity** is the channel usage/ownership discipline. Distinct formal channel parameters cannot be mapped to the same existing channel: the mapping must be injective, because channel use is linear. The implementation layer responsible for enforcing this restriction remains unverified. More generally, a process may finish only when its channel protocols permit completion and all linear obligations have been discharged; the type checker rejects an attempted completion while a provider-channel protocol remains unfinished. The full formal invariant and its application across constructs still need to be written down; do not infer them solely from the `Link` operation.

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
| Process | General umbrella term; interpret in context rather than equating it only with a name or a running instance. |
| Named process | A process referred to by name. |
| Process declaration | The process interface, including its provider-role and client-role channel placeholders. |
| Process definition | The body or expression specifying process behavior. |
| Process incarnation | One running instance of a process. |
| Channel placeholder | A syntactic name intended to be associated with a channel; not the channel resource itself. |
| Session type | The allowed channel protocol, described from the provider endpoint's point of view; type checking accounts for the client role. |
| Residual session type | The part of that protocol still to be performed at the current point. |
| Linearity | Channel usage/ownership discipline; distinct formal channel parameters must map to distinct existing channels, and process completion requires all linear obligations to be discharged. The full formal invariant remains to be written down. |
| Polarity | An implementation-level positive/negative/neutral classification used by the type checker; not a complete explanation of operational behavior. |
| Snapshot | An implementation concept that may relate to the publication's `configuration` and `environment`; the exact mapping is an open hypothesis, not an established equivalence. |
| Turn | Do not treat as a general language-level concept unless a distinct meaning is established. The implementation uses turn-like records for pending communication/exchange state; their precise semantics remain open. |

### Terminology correspondence: OrgLang, publication, and implementation

Use one row for one proposed correspondence. **Mapping status** describes the strength of that correspondence, not the evidence status of a claim or the implementation status. Use three values:

- **Confirmed** — the correspondence is supported by sufficient evidence.
- **Provisional** — evidence supports the correspondence, but it still needs verification.
- **Unresolved** — no correspondence is established, or sources appear to conflict. Describe any discrepancy in **Notes**.

| OrgLang term / concept | Publication term / notation | Implementation name | Mapping status | Notes |
|---|---|---|---|---|
| Provider channel placeholder | Provider-role channel parameter in the process interface | `LiabVar` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| Client channel placeholders | Client-role channel parameters in the process interface | `AssetVars` in `DecSpec` | Provisional | The implementation comment supports this interpretation; verify the full resolution path. |
| `InternalCall` provider channel (`X`) | No equivalent established in the inspected excerpt | `LinkSpec.X` (AST spelling: process-expression `Link`) | Unresolved | Intended to denote the existing provider channel, but the field is typed as `identity.ADT`, not a channel-placeholder symbol. Runtime resolution is unverified. |
| `InternalCall` client channels (`Ys`) | No equivalent established in the inspected excerpt | `LinkSpec.Ys` (AST spelling: process-expression `Link`) | Unresolved | Intended to denote client channels in declaration order; representation and runtime resolution are unverified. |
| `ExternalCall` | `a ← p b`; publication substitution rule | `CallSpec`, `ProcTermQN`, `ValChnlPHs`, `ContExp`, `NewChnlPH` | Provisional | Publication supports invocation and substitution; see Section 7 for the intended contract and Section 14 for unresolved details. Implementation mapping remains unverified. |
| `InternalCall` | No equivalent established | `LinkSpec` (process-expression AST `Link`) | Unresolved | Intended to transfer an existing channel into a fresh incarnation and transfer provider responsibility to it; no complete adapter/executor path was found. |
| Send/publish action (`pub`) | `msg` | `PubRec`, `ValExp` | Provisional | The names align with the send/message side in the described forwarding trace; end-to-end state semantics remain open. |
| Service/wait action (`sub`) | `srv` | `SubRec`, `ContExp` | Provisional | The names align with the service/waiting side in the described forwarding trace; end-to-end state semantics remain open. |
| Residual session type | Remaining protocol after an interaction step | Current session-type value / checker context (`LinearVars`) | Unresolved | Conceptual correspondence only; state-update invariants remain open. |

Preserve mismatches among OrgLang terminology, publication terminology, and implementation names instead of treating them as synonyms by default. Intended behavior is described in Section 7; implementation findings and remaining questions are separated in Part III.




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

The arrows mean “then”; they are explanatory notation, not literal OrgLang syntax. “Transferred” means the matching send/receive actions have both taken place, not merely that one side has started its action. This is a conceptual trace showing how the shared protocol's residual state advances as each side performs its permitted action. A channel is not just a wire carrying arbitrary messages: its session type limits which interaction is allowed next.

**Connection to the implementation vocabulary:** at the process-expression level, the request and response correspond conceptually to complementary `Send`/`Recv` actions, followed by the protocol's finishing actions. Section 10 records the observed checker correspondence for `Send`, `Recv`, and `One`; it is not a complete typing derivation. This example deliberately does not assign a concrete OrgLang session-type expression to the whole protocol, because the exact typing rules and context updates are not yet fully established. It also does not illustrate channel transfer (`Tensor`/`Lolli`) or labelled choice (`Plus`/`With`); those are separate protocol forms discussed in Section 6.

## 4. Process declarations and definitions

Recall the recipe analogy from Section 2: a named process is like a recipe, and each run is an incarnation of that process. A **process declaration** describes the recipe's interface—the channels it expects, including one provider channel and any channels it uses as a client. A **process definition** supplies the implementation—the expression or process body that carries out the work. The distinction matters because a declaration can exist even when the repository does not establish that a usable body is stored or can be loaded. Go-specific names for these concepts are introduced in Part III.

## 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Process control:** `ExternalCall` and `InternalCall` are the two named-process operations described here. Both create a fresh process incarnation. `ExternalCall` creates a fresh provider channel and delivers it outward to the caller; `InternalCall` injects an existing channel inward into the new incarnation, transferring provider responsibility. Intended transitions are described in Section 7.

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The full constructor/field inventory is in Part III.

## 6. Session types: the protocol for a channel

A session type describes the allowed protocol from the provider endpoint's point of view; the type checker accounts for the client role when checking the other endpoint (Section 2). For the request/response example and residual session types, see Section 3.

A protocol can also pass a channel between processes. The sender gives the other process a channel it can use to communicate; the receiver gains access to that channel for the rest of its process. The implementation names the relevant session-type forms `Tensor` and `Lolli`. At a high level, these are the two complementary forms used to describe channel transfer together with the protocol that remains after the transfer. The names alone do not tell the reader which endpoint performs which action: Section 9 records the observed polarity assignments and checker coverage, while Section 10 describes the typing interface. The exact direction mapping remains deliberately unstated here.

Protocols may also allow a choice between labelled alternatives: the implementation uses `Plus` and `With` for the two complementary type forms associated with such choices. `One` represents a finished protocol. The implementation contains `Up` and `Down` too, but their meaning in OrgLang is still being investigated; see Section 9 for observed checker coverage and Section 14 for open questions. The name `Link` is overloaded: **type-level `Link`** is a session-type constructor referring to another type definition; the process-expression AST still uses the implementation spelling `Link` for the operation named **`InternalCall`** in this terminology (Section 7).

This introduction explains why these forms are useful; it is not a complete theory of session types. Part III contains the constructor inventory, observed polarity assignments, checker coverage, and open questions.

## 7. Intended semantics of named-process operations

**This is the canonical statement of the intended language-level behavior.** The comparison with the publication and the implementation notes below provide evidence and caveats; they should not be read as alternative definitions of these operations. Implementation field names are not OrgLang keywords; their correspondence to language-level roles is documented in Section 9.

This section distinguishes two kinds of uncertainty:

- **Intended but underspecified:** the broad behavior is stated here, but its precise rule, conditions, or edge cases still need to be written down and checked.
- **Design question:** the available evidence does not settle which behavior or mechanism OrgLang should choose. This needs an explicit design decision, not just a more precise description.


### `ExternalCall`

**Before:** the caller is executing an `ExternalCall` expression, with its current channel environment and a continuation `ContExp` (the implementation field for the expression the caller should continue with).

**Agreed semantic contract (authoritative language source not yet verified):** resolve the named process and explicitly map every channel parameter in its declaration to an existing channel supplied in the call's environment/arguments. Type checking must verify that each supplied channel's current session type is compatible with the session type required by its corresponding formal parameter, accounting for the roles of the caller and the formal parameter. It must also verify that the provider-oriented session type associated with the new incarnation's provider channel is compatible with the provider-oriented session type assigned to the caller's channel placeholder, accounting for the caller's client role. The exact compatibility rules remain to be formalized. Then start a fresh incarnation with its own separate execution state and channel environment. The formal parameter names are local to that incarnation: the mapping associates them with existing channel identities, but does not transfer the caller's channel names. The explicitly mapped channels are transferred for use by the new incarnation; the separately injected provider channel is the channel through which it communicates with the caller. Distinct formal channel parameters must map to distinct existing channels; mapping two parameters to the same channel is disallowed by linearity. The layer that enforces this restriction is not yet established. `ExternalCall` itself does not implicitly allocate a replacement channel for an omitted parameter.

**After:** once the new incarnation has started, the `ExternalCall` operation is complete and the caller's continuation `ContExp` can proceed; completion does not wait for interaction over the called incarnation's provider channel to finish. The caller names a channel placeholder for the called incarnation's provider channel, and the engine injects that channel into the placeholder. The placeholder's type specifies the provider-oriented session type expected by the caller for this channel. This channel is distinct from the channels explicitly mapped to the callee's formal parameters. The caller uses the client endpoint of this channel and interacts with the called incarnation according to that channel's protocol; the protocol determines when the channel is closed, rather than a separate closure requirement imposed by `ExternalCall`. The general linearity and process-completion rule in Section 2 applies to this channel as well. Each explicitly mapped channel retains its identity and protocol state, but its use is transferred fully to the new incarnation as part of a successful `ExternalCall`; the caller can no longer use that channel afterward. This transfer does not create a copy of the channel. The separately injected provider channel remains the communication channel between the caller as client and the new incarnation as provider.

**Semantic/evidential status:** the completion point of `ExternalCall`, placeholder injection, channel transfer, and caller/client role are agreed as the intended contract in this discussion; they have not yet been verified against an authoritative OrgLang semantic source. **Internal consistency issue:** the preceding `After` paragraph says the caller continuation can proceed once the incarnation has started, while the lifecycle paragraph below says it becomes eligible only when the provider channel is received. These are different completion points; neither should be treated as settled until the intended contract is chosen and checked against the source discussion. **Implementation status:** unverified; the current executor has no `ExternalCall` branch. The exact argument syntax and the mapping of `NewChnlPH` remain open. How this contract maps to `CommChnlPH`, `ValChnlPHs`, and `NewChnlPH` also remains to be verified. This description does not assume that `ExternalCall` is implemented using `Spawn`.

**ExternalCall lifecycle and pending-channel custody (working rule):** an external call has three conceptual stages: initiated, pending, and serviced. Accepting or recording a request is not completion. When a call is initiated, the engine temporarily takes custody of the channels explicitly mapped to the new incarnation's formal parameters (these are client channels relative to that incarnation); while the call is pending, the caller cannot use those channels, and the engine preserves them without participating in their protocols or changing their state. A serviced call creates a fresh incarnation and makes its provider channel available to the caller through the designated placeholder. The caller's continuation becomes eligible to proceed when it receives that channel, not merely when the incarnation is created. The caller does not wait for the callee to terminate, and no scheduling priority or strict execution order between the callee and caller continuation is implied; they may execute in either order or interleave, subject to protocol and linearity constraints. Every successfully serviced call creates a fresh incarnation; reuse of an existing incarnation is not implicit. These are working rules, not verified normative language rules. See [the canonical intended semantics in Section 7](#7-intended-semantics-of-named-process-operations) and [issue #85: Call versus internal spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893).

### `InternalCall`

**Before:** the invoking process provides a service on an existing channel (AST field `X`). The target process also receives a list of channels it will use as a client (AST field `Ys`). The terms *provider channel* and *client channels* are relative to the process being described; they do not imply different kinds of channel resource. The role descriptions are explanatory labels, not claims about how the runtime resolves the fields.

**Preconditions (provisional):** the target process definition must be available and a fresh incarnation must be creatable. Other validity conditions—including whether channel/protocol compatibility is required and where it is checked—remain open. Do not infer a specific residual-session-type equality condition from the current evidence.

**Intended transition:** start a fresh incarnation of the named process, passing the existing provider channel as the target incarnation's provider channel and the specified client channels as channels it uses as a client, in declaration order. Transfer provider-side responsibility for the existing provider channel to the new incarnation. These details describe the current target contract and still require verification against authoritative language sources.

**After (intended):** the new incarnation provides the existing provider channel; the old incarnation has no ordinary continuation. Whether the existing channel's client endpoint and all associated protocol state remain unchanged is part of the contract to verify.

**Mini-example (schematic, not OrgLang syntax):** suppose process `Old` provides channel `c`, and the client has already sent a request. `Old` performs `InternalCall` to process `New`, passing `c`. The intended handoff is that `New` takes over provider responsibility for the existing channel rather than creating an unrelated new interaction. This example does not assume a particular type-equality condition or prove how compatibility is checked.

**Atomic handoff (provisional working rule):** the intended transition is atomic with creation of the new incarnation: the new incarnation is not observable without the transferred channels, and channel transfer does not occur without creating that incarnation. It receives the existing provider channel and every specified client channel in declaration order. The existing provider channel becomes the target incarnation's provider channel; the target inherits its protocol state unchanged and starts at the beginning of the target process body. The old incarnation loses access to all transferred channels, has no channels left in its environment, and cannot continue executing or service the provider channel concurrently with the new incarnation. Do not assign it a lifecycle label such as “terminated” or “suspended”; its subsequent status remains open. These are working rules in the research draft, not verified implementation behavior. Pool association and selection are specified separately in [spawn-semantics, Section 6](../about-spawn/README.md#6-next-semantic-questions).

**Status:** the handoff interpretation is provisional; the exact preconditions, lifecycle guarantees, and representation are not established by the inspected evidence. The current dispatcher has no `InternalCall` execution branch, so this document does not claim that the implementation performs or type-checks this transition. See Section 14 for the unresolved lifecycle and representation questions. This contract does not assume that `InternalCall` is implemented using `Spawn`.

### Boundary with pool semantics

Process invocation and incarnation creation are distinct from the pool mechanism that services a provider channel. An `ExternalCall` or `InternalCall` does not, by itself, require a transaction through the pool's public channel or entry into its critical section; conversely, the pool's `Up … Down` protocol does not imply a process call or incarnation creation. The pool's public channel belongs to the pool, not to an individual process incarnation. Pool association, selection, and eligibility are pool-level concerns documented in [spawn-semantics, Sections 4 and 6](../about-spawn/README.md#4-pool-public-channel-and-callees-private-communication-channel). Negotiation, reservation, failure behavior when no eligible pool exists, and resource provisioning remain underspecified. See also the [issue #85 proposal concerning the pool's offer channel](https://github.com/orglang/go-workspace/issues/85#issuecomment-6231176672).

### `Fwd`

**Purpose:** connect the interaction on one existing channel to the interaction on another. This is an endpoint-level connection, not a named-process invocation. The publication illustrates it with a unit message pending on `c` and a receiver waiting on `d`; see Section 8 for the trace.

**Intended but underspecified:** `Fwd` needs a complete transition rule for channel polarity, pending turns, and continuation state. Polarity is defined in Section 2; Section 9 records the checker's observed assignments. The implementation's turn-like records appear to represent pending communication/exchange state, but `turn` is not used here as a synonym for a communication step. The exact semantics remain open. The publication example and inspected executor do not settle all OrgLang cases; see Section 14 for the canonical open question.

### Summary: compare the three operations

`ExternalCall` and `InternalCall` are distinct named-process operations with different channel effects and continuation behavior. Record each operation's OrgLang meaning, publication interpretation, and implementation behavior separately. `ExternalCall` starts a named-process incarnation with a fresh provider channel and preserves a continuation for the caller; `InternalCall` starts a named-process incarnation and injects an existing channel into it, transferring provider responsibility with no ordinary continuation for the old incarnation; `Fwd` connects two existing channel interactions and does not itself imply a named-process invocation.

| Operation | Primary role | Intended process-control effect | Intended channel effect | Semantic/evidential status | Implementation status |
|---|---|---|---|---|
| `ExternalCall` | Create and invoke a named-process incarnation with a fresh provider channel. | A fresh incarnation starts while the caller's continuation may proceed. | Explicit parameter mapping; a fresh provider channel is delivered outward to the caller. | Agreed intended contract; implementation mapping remains open. | Unverified; no executor branch found. |
| `InternalCall` | Create a named-process incarnation by injecting an existing channel inward. | A fresh incarnation takes over; the old incarnation has no ordinary continuation. | The existing channel resource and its client endpoint remain connected; provider responsibility transfers to the new incarnation. | Inferred target contract; lifecycle and representation open. | Unverified; no complete executor path found. |
| `Fwd` | Connect two existing channel interactions. | No named-process incarnation or named-process continuation transfer is implied. | Relates existing endpoints; no global renaming is implied. | Intended rule open beyond the documented example. | Partial; full symmetric behavior not established. |

Use this table as the quick comparison, and the operation-specific subsections above for the intended transitions and preconditions. Part II gives publication context; Part III records implementation evidence. Those evidence sources are not alternative definitions of the intended behavior.

## Part II. Comparison with the publication

## 8. Comparison with the supplied publication

The supplied publication gives the named-process call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here `p` names the definition, and the rule substitutes actual channel names for the corresponding formal names.

Table 4.2 likewise describes `a ← p b` as a call to named process `p`, which may communicate along channels `a` and `b`. This supports the reading of the construct as named-process invocation and channel substitution. **It does not specify OrgLang's full `ExternalCall` transition or establish that the caller continues through OrgLang's `ContExp`.** For the intended OrgLang contract, use Section 7; keep the publication's rule as supporting context, not proof of the whole contract.

Do not conflate named-process call with the separate cut/spawn rule `x ← P ; Q`. The latter has an inline process body `P`, a continuation `Q`, and explicitly allocates a fresh channel shared by the two resulting processes.

### The publication's cut/spawn rule

The publication separately describes cut/spawn as allocating a fresh channel shared by a spawned process and the original process's continuation. The detailed rule and its limits as evidence for OrgLang are documented in [about-spawn, Section 2.2](../about-spawn/README.md#22-existing-rationale-publication-cutspawn-rule). This comparative rule does not by itself establish OrgLang's `Spawn` semantics.

The publication also gives the following forwarding rules. The mode parameter `m` is omitted here to keep the discussion focused on forwarding rather than channel modes:

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

The publication's `msg` action is tentatively aligned here with OrgLang's `pub` (publish/send a message), and `srv` with `sub` (subscribe/wait to receive or serve); these mappings remain provisional rather than established synonyms. In the inspected implementation, `PubRec` stores a `ValExp` (publication/message action) and `SubRec` stores a `ContExp` (subscription/service continuation). The `Fwd` executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

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

In Section 7, `ContExp` is discussed as the continuation field on the implementation's `CallSpec`; its exact mapping to the language-level `ExternalCall` contract remains unverified. `NewChnlPH` is an implementation field whose relationship to the agreed explicit mapping of parameters to existing channels remains unverified. Its name alone does not establish that `ExternalCall` allocates a channel beyond the intended contract described in Section 7. For `InternalCall` (represented by process-expression `Link` in the AST), `X` is intended to identify the existing provider channel being handed off, and `Ys` the client channels passed to the new process. However, `LinkSpec.X` and `LinkSpec.Ys` are typed as `identity.ADT`, not `symbol.ADT`; the AST therefore does not represent them using the same type as the channel placeholders elsewhere. Here “placeholder” describes their intended language-level role, not a confirmed implementation representation. The actual resolution path remains unverified.

Comments in `proc/termdec/core/core.go` support these readings. For `InternalCall` (represented by process-expression `Link` in the AST), the intended mapping is the provider channel (`X`) → `LiabVar` and each client channel (`Ys[i]`) → `AssetVars[i]` in declaration order. The language-level description uses provider and client roles.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/`Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. The field-type mismatch described above is an implementation discrepancy, not the semantic definition. Related identifiers include:

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
| `Send` | `Tensor` | `Lolli` | Confirmed |
| `Recv` | `Lolli` | `Tensor` | Confirmed |
| `Lab` | `Plus` | `With` | Confirmed |
| `Case` | `With` | `Plus` | Confirmed |
| `Close` / `Wait` | `One` on the corresponding endpoint side | `One` on the corresponding endpoint side | Unverified |
| `Fwd` | compatibility/polarity checks exist | full symmetric behavior not established | Partial |

This table records checker observations, not complete typing rules. Exact side conditions, context splitting, substitution, and freshness conditions remain outside its scope.

**Potential checker issue to verify:** in `proc/compexec/core/core.go`, the `CaseSpec` branch iterates over the type's choices, updates `procCtx.Liabs[expSpec.CommChnlPH]`, and recursively checks each branch using the same mutable context maps. Recursive checks can themselves update those maps (for example, `Send` advances the channel type). No branch-local copy or reset is visible in this path. This may let checking one branch affect the next branch's starting context. Confirm with a focused test where multiple labels have distinct continuations before treating it as a bug.

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

The first fully formalized implementation-level rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. Complete implementation-level reduction rules for `ExternalCall`, `InternalCall`, and resource-management constructs should remain unspecified until the execution paths have been verified and reconciled with the intended contract in Section 7. `Spawn` is deferred to the pool-level analysis. `Link` should be investigated alongside recursive process definitions/calls, not conflated with `Fwd`.

### Named-process operations: implementation evidence

This subsection records implementation findings for `ExternalCall` and `InternalCall` (represented by AST constructors `CallSpec` and `LinkSpec`) and for process creation. Section 12 lists conversion discrepancies; Section 14 is the canonical list of unresolved questions.

**Implementation observation:** the inspected `takeWith` dispatcher has execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. It has no branch for the AST constructs `Call`, `Spawn`, `Link`, `Acqure`, `Accept`, `Detach`, or `Release` in the inspected version. This describes the current dispatcher, not the language design.

The inspected `call` scenario in `test/e2e/pool_test.go` is inconclusive: the top-level `TestPool` does not run the subtest, its result assertion is a TODO, and the callee declaration has no corresponding process body. The process-definition persistence methods inspected so far also appear to be stubs. Thus the repository evidence does not demonstrate a successful transition for the AST `CallSpec` construct associated with `ExternalCall`. See Section 14 for the unresolved argument-mapping question.

**Implementation observation:** `InternalCall` is represented by process-expression `Link` in the AST. Its `X` (provider channel) and `Ys` (client channels) are intended to identify caller-side channels, but the AST types them as `identity.ADT` channel identifiers rather than `symbol.ADT` placeholder names. No complete adapter or executor path was found. The AST `CallSpec` has an explicit `ContExp`; `LinkSpec` does not. See Section 14 for the open lifecycle and representation questions.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. This implementation-level API name is not evidence that OrgLang exposes a user-written `Spawn` operation. The repository contains three distinct `Spawn` representations; they should not be treated as one implementation:

- **Process-expression AST — `SpawnSpec`:** carries a communication-channel placeholder, process-term name, new-channel placeholders, and continuation. The inspected dispatcher has no execution branch; an older `SpawnSpecOld` branch remains commented out.
- **Pool API — `SpawnSpec2`:** names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but does not itself instantiate a process body or wire the fresh channel described by the publication's cut rule.
- **Separate prototype — `proto/rast2` `spawn` reduction:** creates a fresh channel and two process entries. This resembles the publication's allocate-and-spawn shape, but is a separate prototype, not evidence for the current AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This is useful comparison context, not evidence that OrgLang exposes a standalone source-level `Spawn`. Recursion through cyclic dependencies among process definitions remains a hypothesis, not an established mechanism.

### Forwarding remains a separate open question

The executor contains a `Fwd` branch. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. The code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads and do not handle `FwdRec` in those switches. It remains unverified whether another part of scheduling and exchange handling covers this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken.

A formal reduction rule should be added after the relevant typing, executor, adapter, and scheduling paths have been checked together.

## 14. Open questions for the next verification pass

The list is ordered by investigation priority, not by semantic importance.

1. **ExternalCall completion point:** Section 7 currently gives two incompatible descriptions: the caller continuation proceeds when the new incarnation starts, or only when the provider channel is delivered. Which is intended, and what source or design decision settles it?
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

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation.

