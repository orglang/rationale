# Processes and session types

> **Status: preliminary research draft.** This document separates intended OrgLang semantics from observations about `orglang/go-engine`. Formal rules should describe language behavior independently of Go structure and field names; implementation notes are included only to track evidence, discrepancies, and questions requiring verification. Syntax present in the AST is not, by itself, evidence that an expression has a complete runtime semantics.

## Part I. Language model

## 1. Scope and evidence

This document focuses on processes and session types. Pool and transaction semantics are not formalized here, although pool-level process creation is considered where necessary to understand the boundary between invocation and spawning.

## 2. Core concepts

OrgLang processes communicate through **channels**. Think of a channel as a connection between two roles: the **provider** offers a service, and the **client** uses it. Each process has one provider channel of its own and can use other channels as a client.

A named process is like a recipe. Each time it is started, that running copy is a **process incarnation**. A **channel placeholder** is a name in the process expression that stands for a channel; while the process runs, an environment tells us which actual channel each placeholder refers to.

A **session type** is the protocol for a channel: it says what kind of interaction is allowed next. The **residual session type** is the part of that protocol still to be performed at the current moment. For example, imagine a channel whose protocol is “send a request, then receive a response, then finish.” Before the request, its residual type describes the whole sequence. After the request has been sent and received, the residual type describes only “receive a response, then finish.” This matters for `Link`: the new process must be ready to continue the conversation **from its current point**, not restart the protocol from the beginning.

**Linearity** means that a channel has exactly one provider and exactly one client; there must not be two competing providers or two competing clients for the same channel. This is why `Link` transfers the provider's responsibility for an existing channel rather than creating a second provider for it.

### Quick glossary

| Term | Meaning in this document |
|---|---|
| Channel | A connection used by two processes to communicate. |
| Provider / client | The two roles on a channel: offering a service / using it. |
| Process incarnation | One running instance of a named process. |
| Channel placeholder | A name in an expression that stands for an actual channel. |
| Session type | The protocol describing which interaction is allowed on a channel. |
| Residual session type | The part of that protocol still to be performed at the current point. |
| Linearity | The invariant that each channel has exactly one provider and one client. |
| Polarity | An implementation-level positive/negative/neutral classification used by the type checker; not a complete explanation of operational behavior. |

The document distinguishes three evidence levels:

- **Confirmed**: directly supported by the inspected implementation or its comments.
- **Tentative**: a plausible interpretation, but the complete call path or invariant has not been verified.
- **Open**: the inspected implementation does not establish the contract.

## 3. A small example: following a channel

Imagine two processes that communicate over one channel:

1. The client sends a request.
2. The server receives that request.
3. The server sends a response.
4. The client receives the response.
5. Both sides eventually finish the protocol.

This is a **conceptual trace**, not literal OrgLang source code. It illustrates the central idea: a channel is not just a wire carrying arbitrary messages. Its session type limits which interaction is allowed next; the meaning of that type as the conversation progresses is explained in Section 2.

## 4. Process declarations and definitions

A **process declaration** describes the channels a process expects: one provider channel and any channels it uses as a client. A **process definition** gives the expression—the process body—that carries out the work. These are different things: a declaration can exist even when the repository does not establish that a usable body is stored or can be loaded. Go-specific names for these concepts are introduced in Part III.

## 5. Process expressions: the main families

For now, it is enough to recognize four broad kinds of process action:

- **Communication:** send or receive a value/channel, or select and handle a labelled choice.
- **Finishing:** close an interaction or wait for the other side to finish.
- **Connecting interactions:** forward between channels.
- **Process control:** invoke a named process with `Call`, or transfer control with `Link`.

The repository also contains AST constructors for `Spawn`, `Acqure`, `Accept`, `Detach`, and `Release`. Their presence in the syntax tree does not establish their user-facing status or runtime behavior. The full constructor/field inventory is in Part III.

## 6. Session types: the protocol for a channel

A session type describes the sequence and choices of interactions allowed on a channel. The constructors found in the implementation include:

- `One`: a protocol that has finished.
- `Tensor` and `Lolli`: forms associated with sending or receiving a channel and then continuing.
- `Plus` and `With`: forms with labelled alternatives.
- `Up` and `Down`: protocol-shifting forms whose detailed role needs further verification in this repository.
- Type-level `Link`: a reference to another type definition, distinct from the process expression also named `Link`.

This is only an orientation, not a complete typing definition. Detailed constructor fields, polarity assignments, checker coverage, and source discrepancies are collected in Part III.

## 7. Intended semantics of named-process operations

**This is the canonical statement of the intended language-level behavior.** The comparison with the publication and the implementation notes below provide evidence and caveats; they should not be read as alternative definitions of these operations.

### `Call`

**Before:** the caller is executing a `Call` expression, with its current channel environment and a continuation `ContExp`.

**Intended transition:** resolve the named process and the caller-supplied channel placeholders, then start a fresh incarnation of the named process with the channels required by its declaration. The call expression also identifies a caller-side placeholder (`NewChnlPH`) through which a channel made available by the call can be used; the precise allocation/injection mechanism and its mapping to the callee's formal channels remain open.

**After:** the new incarnation can execute independently. The original caller remains active and continues with `ContExp`. Any existing channels passed as arguments retain their identity; this description does not imply that they are replaced.

**Still unspecified:** the exact mapping and ordering between OrgLang's channel-argument fields and the target declaration's formal channels, and exactly how the channel associated with `NewChnlPH` is created or injected. This is the intended OrgLang contract, not a behavior proven by the current executor or by the publication's call rule. It does not assume that `Call` is implemented using `Spawn`.

### `Link`

**Before:** the invoking process is providing a service on channel `X`, with caller-side placeholders `X` and `Ys` resolved in its channel environment.

**Preconditions:** the target process definition is available and a fresh incarnation can be created. The channel supplied by `X` must have the same **current residual session type** as the target process's provider channel—not merely the same initial declared type. In plain terms, both sides must agree on what is supposed to happen next in the conversation. If the existing channel has already passed the request step, the new process must be ready for the response step, not for a new request.

**Intended transition:** start a fresh incarnation of the named process, passing `X` as its provider channel and the channels named by `Ys` as its client channels, in declaration order. Transfer provider-side responsibility for the existing channel `X` to the new incarnation.

**After:** the channel itself and its existing client connection remain unchanged; the new incarnation provides that same channel. Control transfers to the new incarnation, and the old incarnation has no ordinary continuation.

**Still unspecified:** when the old incarnation's remaining state is reclaimed, and how scheduling or failures are handled. This contract does not assume that `Link` is implemented using `Spawn`.

### `Fwd`

**Purpose:** connect the interaction on one existing channel to the interaction on another. Forwarding is an interaction between channel endpoints, not a global renaming of channel identifiers and not, by itself, a named-process invocation.

**Operational intuition:** in the publication's example, a sender has a unit message pending on `c`, a receiver is waiting on `d`, and forwarding connects the waiting interaction on `d` to `c`. The waiting interaction can then receive the message on `c` and continue.

**Still unspecified:** a complete OrgLang transition rule covering both polarities, all pending-turn cases, and the resulting continuation state. The publication example illustrates the intended idea, but the inspected executor contains TODOs and has not been shown to implement every case correctly.

### Summary

| Operation | Process state after the operation | Channel identity and connection | Caller continuation |
|---|---|---|---|
| `Call` | A fresh named-process incarnation starts independently. | Existing argument channels retain their identity; the channel exposed through `NewChnlPH` has unresolved allocation/mapping details. | Continues with `ContExp`. |
| `Link` | A fresh named-process incarnation takes over provider responsibility. | Existing provider channel `X` and its client connection stay the same. | No ordinary continuation. |
| `Fwd` | No named-process incarnation is implied by the operation itself. | Relates two existing channel interactions; no global rename is implied. | Not specified as a named-process continuation transfer. |

The table is the short reference. The detailed claims above are intended semantics; the later sections distinguish what the publication supports and what the current implementation actually demonstrates.

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

The author also supplied these publication forwarding rules. The mode parameter `m` is omitted here to keep the discussion focused on forwarding rather than channel modes:

    proc(d⁺ ← c⁺) → !⁺msg(d⁺, c⁺)   id: forward+
    proc(d⁻ ← c⁻) → !⁻srv(d⁻, c⁻)   id: forward−

In OrgLang, the publication's msg maps to pub, and srv maps to sub. In the inspected implementation, PubRec stores a ValExp (publication/message action) and SubRec stores a ContExp (subscription/service continuation). The Fwd executor examines channel polarity and pending communication turns, redirecting the relevant turn; if none is pending, it records a publication or subscription turn carrying a forwarding record. Some source branches still contain TODOs, so this is not a complete correctness proof.

### Reading the publication's forwarding example

The publication's Example 9 gives a concrete positive-polarity trace. A sender publishes the unit value `()` on `c`; a receiver is waiting on `d`; and a forwarding process connects the two. The receiver first becomes a service waiting on `d`. The forwarding process then produces a forwarding message for the pair `(d, c)`. When that forwarding message meets the service waiting on `d`, the service is redirected to wait on `c`; the sender's pending unit message can then be received, and the receiver continues as `P`.

The important point is that forwarding is shown as an interaction between a forwarding message and a waiting service, not as a global renaming of every occurrence of `d` to `c`. The trace also shows that the receiver may need another evaluation step to begin listening again after its service has been redirected.

Neither this example nor the other discussion in this section establishes that OrgLang's `Link` is equivalent to `Call` followed by `Fwd`.

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

A process declaration is represented by `DecSpec` with fields:

- `TermQN`: the declaration's qualified name;
- `LiabVar`: the provider-channel placeholder in the declaration;
- `AssetVars`: the client-channel placeholders in the declaration.

These interpretations are supported by comments in `proc/termdec/core/core.go`. For language-level `Link`, the intended mapping is that `X` supplies the channel for `LiabVar`, and `Ys[i]` supplies the channel for `AssetVars[i]` in declaration order. These are implementation field names; the language-level description uses provider and client channels instead.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/`Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. In particular, `LinkSpec.X` and `LinkSpec.Ys` are `identity.ADT` values, not channel placeholders (`symbol.ADT`). The author has clarified their intended language-level meaning as caller-side channel placeholders; the Go field types are an implementation discrepancy, not the semantic definition:

- `TermQN`: qualified name associated with a declaration;
- `ProcQN`: qualified name associated with a definition;
- `ProcTermQN`: name referenced by call/spawn expression constructors;
- expression identity / `valkey`: a candidate identifier for an expression incarnation, whose exact lifecycle remains to be confirmed.

Do not assume these identifiers are interchangeable.

### Appendix A. Detailed AST and session-type inventory

#### A.1 Process-expression AST inventory

The inspected process AST defines the following constructors and fields:

| Constructor | Fields observed | Intended reading (provisional where noted) |
|---|---|---|
| `CloseSpec` | `ContChnlPH` | Close/terminate a session endpoint |
| `WaitSpec` | `ContChnlPH`, `ContExp` | Wait on an endpoint, then continue |
| `SendSpec` | `CommChnlPH`, `ValChnlPH` | Send a channel/value over a communication endpoint |
| `RecvSpec` | `CommChnlPH`, `NewChnlPH`, `ContExp` | Receive and bind a channel, then continue |
| `LabSpec` | `CommChnlPH`, `ValLabQN`, `ContExp` | Send/select a label; the AST also carries a continuation, though its use needs verification |
| `CaseSpec` | `CommChnlPH`, `ContExps` | Offer branches indexed by labels |
| `LinkSpec` | `ProcTermQN`, `X`, `Ys` (`identity.ADT`) | Named-process construct with no `ContExp`. This distinguishes it from `CallSpec`; do not unify the syntax without accounting for the different continuation/control-flow behavior |
| `FwdSpec` | `CommChnlPH`, `ContChnlPH` | Forward between endpoints |
| `CallSpec` | `CommChnlPH`, `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp` | Candidate representation of a named-process call. Unlike the supplied publication's call form `a ← p b₁ … bₙ`, this AST carries a continuation and distinct channel placeholders; their semantic roles are not yet established |
| `SpawnSpec` | `CommChnlPH`, `ProcTermQN`, `NewChnlPHs`, `ContExp` | Present in AST, but excluded from the current process-semantics scope pending pool-level analysis |
| `AcqureSpec` | see source | Constructor spelling as present in code; contract open |
| `AcceptSpec` | see source | Contract open |
| `DetachSpec` | see source | Contract open |
| `ReleaseSpec` | see source | Contract open |

The table is a syntax inventory, not a claim that all constructors are executable.

#### A.2 Session-type AST and checker coverage

The process session-type AST contains these constructors:

| Type constructor | Fields observed | Polarity recorded by the type checker |
|---|---|---|
| `OneSpec` | none | positive |
| `TensorSpec` | `Val`, `Cont` | positive |
| `LolliSpec` | `Val`, `Cont` | negative |
| `PlusSpec` | `Choices` | positive |
| `WithSpec` | `Choices` | negative |
| `UpSpec` | `Cont` | zero / neutral |
| `DownSpec` | `Cont` | zero / neutral |
| `LinkSpec` | `TypeQN` | zero / neutral |

The polarity assignments above reflect the inspected implementation in `proc/typeexp/core/core.go`; they should not be read as a complete typing definition. Here, **polarity** is the implementation's positive/negative/neutral classification of a session type. It is relevant to how the implementation handles a protocol action, but the table alone does not explain or prove all operational cases.

At the AST level, process `Plus`/`With` choices are represented as label-indexed alternatives. The exact normalization and lookup rules for type references, and how `Up`/`Down` are unfolded, remain to be confirmed.

The current process-level `CheckSpec` and `CheckRec` implementations explicitly handle only `One`, `Tensor`, `Lolli`, `Plus`, and `With`; any other expected constructor reaches the default panic. In contrast, the pool-level type-expression conversion includes `Link`, `Up`, and `Down` cases. This is evidence that the repository has multiple layers with different constructor coverage, not proof that the process checker is reached with unresolved `Link`/`Up`/`Down` in ordinary execution.

One concrete source discrepancy exists in `pool/typeexp/core/tc.go`: the `DownSpec` conversion constructs and returns `UpRec` rather than `DownRec`. Also, the `PlusSpec` conversion composes a value key but does not check/return the `Compose` error in the same way as neighboring branches. These are implementation findings only; they should be validated with focused tests and should not be used to define the intended type semantics.
## 10. Typing interface

### What type checking does

Before an expression is executed, the implementation checks whether the current channel protocols fit the operation. For example, a send action should only be used when the channel's current protocol permits sending; a close action should only be used when that interaction is ready to finish. These are intuitive explanations, not complete formal rules.

In the implementation, `proc/compexec/core/core.go` loads the current execution snapshot, gathers relevant process declarations and type definitions, builds the type-checking context, and calls `checkType` before dispatching the expression. The snapshot is the saved state of the current computation; its `LinearVars` map records the channel variables tracked by the checker. The exact invariants of this context still need verification.

### How to read the correspondence table

The table records which session-type constructor the inspected checker expects for each process operator. “Provider-side” and “client-side” identify the two channel roles described in Section 2; they do not mean that the whole process has two provider channels. A match in this table is evidence about the checker, not a complete language rule.

| Process operator | Provider-side expectation | Client-side expectation | Evidence status |
|---|---|---|---|
| `Send` | `Tensor` | `Lolli` | observed in checker branches |
| `Recv` | `Lolli` | `Tensor` | observed in checker branches |
| `Lab` | `Plus` | `With` | observed in checker branches |
| `Case` | `With` | `Plus` | observed in checker branches |
| `Close` / `Wait` | `One` on the corresponding endpoint side | `One` on the corresponding endpoint side | exact side-specific conditions should be rechecked |
| `Fwd` | compatibility/polarity checks exist | full symmetric behavior not established | partial |

This table is intentionally not a formal typing judgment. It leaves out the exact conditions that must hold before a rule applies, how channel variables are divided between subexpressions (often called *context splitting*), and how names are substituted or checked for freshness.

The inspected checker explicitly handles `One`, `Tensor`, `Lolli`, `Plus`, and `With`. Its default branch appears to panic for `Link`, `Up`, and `Down`, which means those forms are not handled at that point in the code. Whether normal execution resolves or unfolds these constructors before this code is reached is an open question, not yet a confirmed runtime bug.

## 11. Execution and communication

At a high level, the inspected execution path follows six steps. The names in parentheses are implementation details:

1. Read the saved state of the computation (the execution snapshot).
2. Gather the process declarations and type definitions needed for the current action.
3. Check that the action fits the channel protocols currently in force (`checkType`).
4. Run the matching handler for the action (`takeWith`).
5. Save the resulting state changes and effects.
6. If the action produced a next expression, schedule or continue with it; otherwise return.

This outline is a map of the observed code path, not a complete definition of when a process blocks, resumes, or owns a channel.

The inspected `takeWith` contains execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. The current `LabSpec` AST includes `ContExp`, but its message adapter does not preserve that field; whether a label-selection continuation is semantically required remains open. It does not contain branches for `Call`, `Spawn`, `Link`, `Acqure`, `Accept`, `Detach`, or `Release`; those constructors have no execution branch in this dispatcher in the inspected version. This is a statement about the inspected implementation, not by itself a conclusion that the language design is defective. `Spawn` and the call mechanism are interdependent because both may rely on the unresolved model of process creation and pools. Consequently, no complete operational rule for `Call` or `Spawn` is specified here. One possibility is that recursion arises from cyclic dependencies among process definitions rather than requiring a separate recursive-call construct; this remains unverified. This does not imply that `Link` and `Call` should be unified: `Call` has an explicit `ContExp`, whereas `Link` does not, and their operational rules must account for that distinction. Channel forwarding (`Fwd`) remains a distinct operation.

Communication may take more than one execution step. If the matching action from the other side is not yet available—for example, the corresponding `Wait` for a `Close`, or a receive for a send—the current action may register that it is waiting and return. When the other side becomes available, the implementation updates the exchange state and channel records, and may schedule the continuation. The precise ordering and ownership rules are still open.

This is an implementation-level description. The exact transition relation, message ownership, and invariants for subscriptions, publications, and exchange turns still need to be formalized from all producer/consumer call paths.

## 12. Representation and serialization caveats

The adapter in `proc/termexp/adapter/tc.go` translates between AST, message, and stored representations. In the inspected version, `MsgFromExpSpec` has no `Link` branch; `MsgToExpSpec` has a `Call` branch, but reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. The executor has no `Call` or `Link` branch. The `call` scenario in `test/e2e/pool_test.go` constructs a caller and a call expression, but the top-level `TestPool` does not run it (the subtest is commented out); the scenario also leaves its result assertion as a TODO and creates the callee declaration without defining a callee body. It therefore does not establish a successful call transition, even if run separately. These observations describe the current implementation and evidence limits; they do not establish that `Call` is independently implementable or that the missing branches are defects, because call semantics may depend on the unresolved `Spawn`/pool model. The adapter also contains these apparent asymmetries:

- `MsgToExpSpec` reconstructs `CallSpec` without `CommChnlPH` and `ContExp`, although those fields exist in the AST constructor. In the current AST, `LabSpec` also has a `ContExp` field; the message conversion reconstructs `LabSpec` without it.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in the message-to-AST conversion and in the stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.

These are source-level discrepancies to validate with focused tests and call-path analysis. Their observable runtime impact is not established by this document.

## 13. Operational semantics: conservative scope

A formal reduction relation should distinguish at least:

- an expression that is ready to execute;
- an expression suspended while waiting for a peer;
- a communication whose peer has arrived;
- the resulting channel/linear-context update;
- continuation scheduling and persistence.

The current evidence supports treating execution as a stateful transition over an execution snapshot plus communication/exchange state. It does **not** yet justify importing a generic session-calculus semantics verbatim, nor asserting that each AST constructor has a complete reduction rule.

The first fully formalized implementation-level rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. A complete implementation-level reduction rule for `Call` and resource-management constructs should remain unspecified until the execution paths have been verified and reconciled with the intended contract in Section 7. `Spawn` is deferred to the pool-level analysis. `Link` should be investigated alongside recursive process definitions/calls, not conflated with `Fwd`.

### Named-process implementation evidence

The current Go AST uses names such as CallSpec, LinkSpec, BindChnlPH/NewChnlPH, and ValChnlPHs. These names describe the present representation; they are not terms in the rules above.

The inspected call example in test/e2e/pool_test.go is inconclusive: its result assertion is a TODO, the callee declaration has no corresponding process body, and the process-definition persistence methods inspected so far are stubs. The adapter maps external BindChnlPH to internal NewChnlPH and does not preserve ContExp when reconstructing CallSpec. Therefore, the current code does not confirm the Section 7 `Call` transition or the mapping of additional channel arguments.

For Link, the intended meaning is that X and Ys name placeholders in the invoking process, but the inspected AST types these fields as identity.ADT channel identifiers rather than symbol.ADT placeholder names. No complete adapter or executor path for Link was found in the inspected code. This is a likely representation inconsistency if placeholder resolution is expected at this stage; the intended fix should not be chosen without tracing where resolution is meant to occur.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. Here, `Spawn` is an implementation-level API name; it is not evidence that the OrgLang source language exposes a user-written `Spawn` operation.

The available code contains multiple incomplete approaches to spawning, which should not be merged into one inferred rule:

- The process-expression AST has a `SpawnSpec` with a communication-channel placeholder, a process-term name, new-channel placeholders, and a continuation. But the inspected process executor has no `SpawnSpec` execution branch; an older `SpawnSpecOld` branch remains commented out in the type-checking/execution code.
- The pool-level `SpawnSpec2` instead names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but the inspected method does not itself instantiate a process body or wire up the fresh channel described by the publication's cut rule.
- A separate prototype under `proto/rast2` has a `spawn` reduction that creates a fresh channel and two process entries. That resembles the publication's allocate-and-spawn shape, but it belongs to a different prototype representation; it does not establish the intended semantics of the current OrgLang AST or pool API.

The publication's cut rule describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. This is useful comparison context, but it is not evidence that OrgLang exposes a standalone source-level `Spawn`; see the distinction in Section 7.

`Fwd` is also represented in the inspected executor. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. However, the code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads and do not handle `FwdRec` in those switches. We have not established whether another part of the scheduling and exchange path handles this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken. Its completeness remains an open question.

## 14. Open questions for the next verification pass

1. What is the precise relationship among TermQN, ProcQN, ProcTermQN, declaration references, and expression identity?
2. What is the intended relationship among process-level invocation, pool-level Spawn, and the pool model?
3. For Call, what are the role and ordering of additional channel arguments, and how do they map to formal channel parameters?
4. Where should name resolution, recursion checks, and type checks be enforced?
5. Are type-level Link, Up, and Down resolved before the currently observed type-checking cases?
6. What are the contracts of Acqure, Accept, Detach, and Release?
7. What are the full invariants for ChnlBS, provider/client orientation, and linear-context updates?
8. Are the conversion asymmetries listed above reachable in actual execution, and which tests can establish their impact?
9. What exact transition semantics do subscription/publication and exchange-turn records implement?
10. Must all branches of a Case preserve equivalent linear contexts, and where is that enforced?
11. What lifecycle, failure, and scheduling guarantees apply when Link transfers control?

## 15. Non-goals

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation.

