# Processes and session types

> **Status: preliminary research draft.** This document separates intended OrgLang semantics from observations about `orglang/go-engine`. Formal rules should describe language behavior independently of Go structure and field names; implementation notes are included only to track evidence, discrepancies, and questions requiring verification. Syntax present in the AST is not, by itself, evidence that an expression has a complete runtime semantics.

## Part I. Language model

## 1. Scope and evidence

This document focuses on processes and session types. Pool and transaction semantics are not formalized here, although pool-level process creation is considered where necessary to understand the boundary between invocation and spawning.

## 2. Core concepts

OrgLang processes communicate through **channels**. Each channel connects one provider, which offers a service, and one client, which uses that service. A process has one provider channel of its own and may use other channels as a client.

A **process incarnation** is one running instance of a named process. A **channel placeholder** is a name used in an expression to refer to a channel; a placeholder environment maps those names to the actual channels in a running process.

A **session type** describes the protocol allowed on a channel. As communication proceeds, the channel reaches a **residual session type**: the remaining protocol at the current point, which may differ from the initially declared type.

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

This is a **conceptual trace**, not literal OrgLang source code. It illustrates the central idea: a channel is not just a wire carrying arbitrary messages. Its session type describes which interaction is allowed next. After each step, the protocol advances to a new residual session type. After the request has been sent and received, for example, the remaining protocol describes the response phase rather than the request phase.

The same view helps distinguish operations. Sending or receiving advances an existing interaction; `Call` starts another process while the caller can continue; `Link` transfers control to a new process incarnation on the caller's existing provider channel; and `Fwd` connects interactions across channels. These operations should not be treated as interchangeable.

## 4. Process declarations and definitions

A process declaration describes the channels a process uses: one provider channel and its client-side channels. A process definition associates a name with the expression that implements the process. Keeping the declaration separate from the definition matters: knowing the declared channels does not by itself establish that a process body exists or can be loaded at runtime.

The implementation uses identifiers such as `TermQN`, `ProcQN`, and `ProcTermQN` for different references. Their exact relationships are documented in the implementation part below; they should not be treated as interchangeable.

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

This section states the intended OrgLang behavior independently of Go structures. The rules are preliminary: they record the design clarified so far, while leaving unresolved details explicit.

### Call

**In simple terms:** `Call` invokes a named process. The caller supplies channel placeholders or arguments according to the named process's declaration, so the new incarnation can interact with its environment through those channels. In our current working model of OrgLang, the invoked process starts executing independently, while the caller continues after the `Call` expression.

This is the current intended language-level behavior, not a description of its implementation. It is consistent with the publication's named-process call `a ← p b`, but the exact mapping and ordering of OrgLang channel arguments remain unspecified. In particular, this definition does not assume that `Call` is implemented using `Spawn`.

### Link

**In simple terms:** `Link` starts a fresh incarnation of a named process and transfers control to it, without an ordinary continuation in the invoking process. The invoking process supplies `X` as its existing provider channel; the new incarnation takes over providing that same channel. The channel and its client connection stay the same.

This is the intended language-level transition; it does not assume that `Link` is implemented using `Spawn`. Although `Link` has some similarities to a tail call and to `Call` combined with forwarding, neither equivalence has been established.

**Preconditions and transition:**

1. The named process definition is available, and a fresh incarnation can be created.
2. Resolve the caller-supplied placeholders in the invoking process's placeholder environment. X supplies the existing provider channel for the target process's LiabVar; each Ys[i] supplies the channel for AssetVars[i], in declaration order.
3. At the point Link is invoked, the target process's provider channel must have exactly the same **current residual session type** as the existing channel supplied by X.
4. Start the fresh incarnation with those channels, transferring provider-side ownership of the existing channel to it. The channel itself and its existing client's connection remain unchanged.
5. Transfer control to the new incarnation. There is no ordinary caller continuation.

The transition preserves linearity: every channel has exactly one provider and one client. This rule does not specify when the old incarnation's remaining state is reclaimed, or define scheduling and failure behavior.

### `Fwd`: intended meaning

In simple terms, `Fwd` connects the interaction on one channel to the interaction on another. It lets a participant waiting on one channel continue through the other channel, so communication can proceed between the parties without treating forwarding as a global renaming of channel identifiers. The exact operational steps depend on the polarity of the forwarding operation.

The publication's example illustrates the idea: one process sends a unit value on channel `c`, while another is waiting on channel `d`. A forwarding operation relating `d` and `c` allows that waiting interaction to reach the message on `c`, after which the receiving process continues. This is the intended reading of the example, not yet a claim that every execution order is correctly handled by the OrgLang implementation.

### Comparing `Call`, `Link`, and `Fwd`

A short comparison helps keep the three ideas separate:

| Operation | What changes? | Does the invoking process continue normally? | What happens to channels? |
|---|---|---|---|
| `Call` | A fresh incarnation of a named process starts. | Yes, according to the current intended OrgLang model. | The caller supplies channels according to the process interface; the exact argument mapping remains open. |
| `Link` | A fresh incarnation takes over providing the caller's existing provider channel, and control transfers to it. | No ordinary continuation is specified. | The provider channel and its client connection stay the same; provider-side responsibility transfers. |
| `Fwd` | Interaction on one channel is connected to interaction on another. | This is not defined as a named-process call or a continuation transfer. | It relates two existing channel interactions; it is not a global rename of channel identifiers. |

For example, if a process needs a helper to perform work and then continue, that is the intended shape of `Call`. If a process has reached a point where another process should take over its provider-side conversation, that is the intended shape of `Link`. If two channel interactions need to be connected so a message or service can pass between them, that is the role of `Fwd`.

These are language-level descriptions. The implementation evidence later in the document does not yet establish complete execution paths for all three operations.

A schematic view (not OrgLang source syntax):

```text
Call:  caller ── invokes ──> fresh process
       caller ── continues through its continuation

Link:  old provider ── same channel ──> new process takes over
       control transfers; no ordinary caller continuation

Fwd:   interaction on channel A ── forwarded to ──> interaction on channel B
       no named-process invocation is implied
```

The arrows summarize the intended distinctions only. They do not specify scheduling order, internal data structures, or a proven implementation strategy.

### User-facing operations and internal process creation

- **Call:** invokes a named process; in the current OrgLang model, the caller continues after the call.
- **Link:** starts a fresh incarnation and transfers provider ownership of an existing channel and control to it.
- **Fwd:** remains a separate forwarding operation. The analogy Link ≈ Call + Fwd is an intuition only, not an established equivalence.
- **Spawn:** treat this as a possible internal process-creation mechanism, not as a user-facing OrgLang operation. Whether, and how, `Call` or `Link` use that mechanism remains unverified. The publication's `cut` rule describes allocate-and-spawn behavior; it does not imply that OrgLang programmers can write `Spawn` directly.

## Part II. Comparison with the publication

## 8. Comparison with the supplied publication

The supplied publication gives the call rule:

    proc(a ← p b) → proc(P[a/x, b/y])

when the definition x ← p y = P is present in the definition environment. Here p names the process definition, and a, b, x, and y are channel names/placeholders in the call and definition. The rule substitutes actual channel names for the corresponding formal names and replaces the call term with the instantiated body in the publication's abstract configuration.

Table 4.2 also lists `a ← p b` as a separate process term: it calls the named process `p`, which may communicate along channels `a` and `b`. This is the publication's named-process call form.

Do not conflate that row with the cut/spawn rule `x ← P ; Q`. In the latter, `P` is an inline process body, `Q` is the original process's continuation, and the rule explicitly allocates a fresh channel shared by the two resulting processes. The table's call row names a process and its channels; it does not itself state the same allocate-channel-and-continue behavior.

The publication's operational call rule below specifies substitution of actual channel names for formal channel names and replaces the call term with the instantiated body in the abstract configuration. It does not explicitly say what happens to a separate calling process or whether it continues. Therefore, use it as evidence for named-process invocation and channel substitution, not as a complete account of OrgLang control flow. OrgLang's currently intended `Call` description—that it starts a fresh incarnation while the caller continues through its continuation—is a language-specific interpretation and should not be presented as directly established by this publication rule.

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
- `LiabVar`: the endpoint on which the process acts as provider;
- `AssetVars`: endpoints on which it acts as client.

These provider/client descriptions come from comments in `proc/termdec/core/core.go`. For `Link`, the author confirms that `Ys[i]` maps to `AssetVars[i]` in declaration order.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/ `Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. In particular, `LinkSpec.X` and `LinkSpec.Ys` are `identity.ADT` values, not channel placeholders (`symbol.ADT`). The author has clarified their intended language-level meaning as caller-side channel placeholders; the Go field types are an implementation discrepancy, not the semantic definition:

- `TermQN`: qualified name associated with a declaration;
- `ProcQN`: qualified name associated with a definition;
- `ProcTermQN`: name referenced by call/spawn expression constructors;
- expression identity / `valkey`: a candidate identifier for an expression incarnation, whose exact lifecycle remains to be confirmed.

Do not assume these identifiers are interchangeable.

### Detailed AST and session-type inventory

#### Process-expression AST inventory

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

#### Session-type AST and checker coverage

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

The polarity assignments above reflect the inspected implementation in `proc/typeexp/core/core.go`; they should not be read as a complete typing definition.

At the AST level, process `Plus`/`With` choices are represented as label-indexed alternatives. The exact normalization and lookup rules for type references, and how `Up`/`Down` are unfolded, remain to be confirmed.

The current process-level `CheckSpec` and `CheckRec` implementations explicitly handle only `One`, `Tensor`, `Lolli`, `Plus`, and `With`; any other expected constructor reaches the default panic. In contrast, the pool-level type-expression conversion includes `Link`, `Up`, and `Down` cases. This is evidence that the repository has multiple layers with different constructor coverage, not proof that the process checker is reached with unresolved `Link`/`Up`/`Down` in ordinary execution.

One concrete source discrepancy exists in `pool/typeexp/core/tc.go`: the `DownSpec` conversion constructs and returns `UpRec` rather than `DownRec`. Also, the `PlusSpec` conversion composes a value key but does not check/return the `Compose` error in the same way as neighboring branches. These are implementation findings only; they should be validated with focused tests and should not be used to define the intended type semantics.
## 10. Typing interface

The execution path in `proc/compexec/core/core.go` loads the current execution snapshot, builds a type environment from relevant process declarations and type definitions, derives a context from the snapshot's linear channel variables, and calls `checkType` before dispatching the expression to the executor.

The snapshot is documented as an execution configuration and contains a `CompRef` plus a `LinearVars` map. This suggests that typing is performed against the current linear-channel context, but the full typing judgment and all context-splitting invariants need to be stated only after checking every constructor and helper.

Observed operator/type correspondences include:

| Process operator | Provider-side expectation | Client-side expectation | Evidence status |
|---|---|---|---|
| `Send` | `Tensor` | `Lolli` | observed in checker branches |
| `Recv` | `Lolli` | `Tensor` | observed in checker branches |
| `Lab` | `Plus` | `With` | observed in checker branches |
| `Case` | `With` | `Plus` | observed in checker branches |
| `Close` / `Wait` | `One` on the corresponding endpoint side | `One` on the corresponding endpoint side | exact side-specific conditions should be rechecked |
| `Fwd` | compatibility/polarity checks exist | full symmetric behavior not established | partial |

This table is intentionally not a formal typing judgment. In particular, it does not specify context splitting, freshness, substitution, or all premises.

The inspected `CheckSpec`/`CheckRec` handling explicitly covers `One`, `Tensor`, `Lolli`, `Plus`, and `With`; `Link`, `Up`, and `Down` appear to reach an unsupported-constructor panic in the default branch. Whether normal execution resolves or unfolds these constructors before this code is reached is an open question, not yet a confirmed runtime bug.

## 11. Execution and communication

At a high level, the inspected `Take` path is:

1. Load the current execution snapshot.
2. Collect the process declarations/type definitions needed by the current expression.
3. Build the type context and run `checkType`.
4. Dispatch the expression through `takeWith`.
5. Persist the resulting modification/effects.
6. If a next expression is scheduled, continue from the updated reference and expression; otherwise return.

The inspected `takeWith` contains execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. The current `LabSpec` AST includes `ContExp`, but its message adapter does not preserve that field; whether a label-selection continuation is semantically required remains open. It does not contain branches for `Call`, `Spawn`, `Link`, `Acqure`, `Accept`, `Detach`, or `Release`; those constructors have no execution branch in this dispatcher in the inspected version. This is a statement about the inspected implementation, not by itself a conclusion that the language design is defective. `Spawn` and the call mechanism are interdependent because both may rely on the unresolved model of process creation and pools. Consequently, no complete operational rule for `Call` or `Spawn` is specified here. Recursion may arise from cyclic dependencies among process definitions rather than requiring a separate recursive-call construct. This does not imply that `Link` and `Call` should be unified: `Call` has an explicit `ContExp`, whereas `Link` does not, and their operational rules must account for that distinction. Channel forwarding (`Fwd`) remains a distinct operation.

Communication is not necessarily completed in one pass. For example, when the counterpart of a `Close`/`Wait` or a send/receive interaction is not yet available, the execution path can register a subscription and return without completing that interaction. When the peer is found, the implementation updates exchange state, allocates channel identifiers, updates linear-variable records, and may schedule the continuation.

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

The first fully formalized rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. Rules for calls and resource-management constructs should remain explicitly unspecified until their intended and implemented contracts are reconciled. `Spawn` is deferred to the pool-level analysis. `Link` should be investigated alongside recursive process definitions/calls, not conflated with `Fwd`.

### Named-process implementation evidence

The current Go AST uses names such as CallSpec, LinkSpec, BindChnlPH/NewChnlPH, and ValChnlPHs. These names describe the present representation; they are not terms in the rules above.

The inspected call example in test/e2e/pool_test.go is inconclusive: its result assertion is a TODO, the callee declaration has no corresponding process body, and the process-definition persistence methods inspected so far are stubs. The adapter maps external BindChnlPH to internal NewChnlPH and does not preserve ContExp when reconstructing CallSpec. Therefore, current code does not confirm the complete call transition or the mapping of additional channel arguments.

For Link, the intended meaning is that X and Ys name placeholders in the invoking process, but the inspected AST types these fields as identity.ADT channel identifiers rather than symbol.ADT placeholder names. No complete adapter or executor path for Link was found in the inspected code. This is a likely representation inconsistency if placeholder resolution is expected at this stage; the intended fix should not be chosen without tracing where resolution is meant to occur.

The pool API has a `Spawn` operation that carries a process declaration reference and optional references to existing process incarnations. Here, `Spawn` is an implementation-level API name; it is not evidence that the OrgLang source language exposes a user-written `Spawn` operation.

The available code contains multiple incomplete approaches to spawning, which should not be merged into one inferred rule:

- The process-expression AST has a `SpawnSpec` with a communication-channel placeholder, a process-term name, new-channel placeholders, and a continuation. But the inspected process executor has no `SpawnSpec` execution branch; an older `SpawnSpecOld` branch remains commented out in the type-checking/execution code.
- The pool-level `SpawnSpec2` instead names a process declaration and optional existing process incarnations. Its `Spawn` method creates a new execution record in linear mode, but the inspected method does not itself instantiate a process body or wire up the fresh channel described by the publication's cut rule.
- A separate prototype under `proto/rast2` has a `spawn` reduction that creates a fresh channel and two process entries. That resembles the publication's allocate-and-spawn shape, but it belongs to a different prototype representation; it does not establish the intended semantics of the current OrgLang AST or pool API.

The publication's cut rule `x ← P ; Q` describes allocating a fresh channel, starting `P[a/x]`, and continuing the original process as `Q[a/x]`. For OrgLang, this is a useful model of the underlying process-creation behavior, but we should not present it as a standalone source-language operation unless syntax or language documentation confirms that programmers can write `Spawn` directly.

`Fwd` is also represented in the inspected executor. When no turn is pending, positive polarity registers a `PubRec` carrying `FwdRec`, while negative polarity registers a `SubRec` carrying `FwdRec`; other branches inspect polarity and the pending turn kind. However, the code contains TODOs for channel-side metadata, and a negative-polarity branch comments on a type mismatch. The ordinary send/receive handlers inspected so far expect `RecvRec`/`SendRec` payloads and do not handle `FwdRec` in those switches. We have not established whether another part of the scheduling and exchange path handles this case. This suggests the implementation may be unfinished, but does not prove that `Fwd` is broken. Its completeness remains an open question.

## 14. Other implementation observations

The inspected process execution path loads an execution snapshot, collects declarations and type definitions, builds a type context, checks the expression, dispatches it, persists the resulting changes, and may schedule a continuation. The dispatcher currently has branches for Close, Wait, Send, Recv, Lab, Case, and Fwd, but not for Call, Spawn, Link, Acqure, Accept, Detach, or Release. This describes the inspected implementation, not by itself a conclusion about the language design.

Other adapter discrepancies observed during inspection include:

- MsgFromExpSpec has no Link branch.
- MsgToExpSpec reconstructs CallSpec without CommChnlPH and ContExp; it also reconstructs LabSpec without its ContExp.
- Case-expression conversions appear to read label data from a fixed Lab field rather than the current branch entry.
- Some send/receive record conversions do not preserve channel fields symmetrically.

These are source-level findings whose runtime impact has not been established. Focused tests and complete call-path analysis are needed before proposing implementation changes. This research task does not modify orglang/go-engine.

## 15. Open questions for the next verification pass

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

## 16. Non-goals

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation.

