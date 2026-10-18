# Processes and session types

> **Status: preliminary research draft.** This document records the current model inferred from the process-related code in `orglang/go-engine`. It is intentionally explicit about uncertainty: syntax present in the AST is not, by itself, evidence that an expression has a complete runtime semantics.

## 1. Scope and evidence

The primary implementation locations inspected for this draft are:

- `proc/termdec/core/core.go`
- `proc/termdef/core/core.go`
- `proc/termexp/core/core.go`
- `proc/typeexp/core/core.go`
- `proc/compexec/core/core.go`
- `proc/termexp/adapter/tc.go`
- `proc/termexp/core/ds.go`

This is a description of the process/session-type layer. Pool and transaction semantics are not formalized here, but pool-level process creation is inspected where necessary to understand the boundary between invocation and spawning.

The terms **confirmed**, **tentative**, and **open** are used as follows:

- **Confirmed**: directly supported by the currently inspected implementation or its comments.
- **Tentative**: a plausible interpretation, but the complete call path or invariant has not yet been verified.
- **Open**: the implementation inspected so far does not establish the contract.

## 2. Process declarations and definitions

A process declaration is represented by `DecSpec` with fields:

- `TermQN`: the declaration's qualified name;
- `LiabVar`: the endpoint on which the process acts as provider;
- `AssetVars`: endpoints on which it acts as client.

These provider/client descriptions come from comments in `proc/termdec/core/core.go`. For `Link`, the author confirms that `Ys[i]` maps to `AssetVars[i]` in declaration order.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/ `Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. In particular, `LinkSpec.X` and `LinkSpec.Ys` are `identity.ADT` values, not channel placeholders (`symbol.ADT`), The author has clarified their intended language-level meaning as caller-side channel placeholders; the Go field types are an implementation discrepancy, not the semantic definition:

- `TermQN`: qualified name associated with a declaration;
- `ProcQN`: qualified name associated with a definition;
- `ProcTermQN`: name referenced by call/spawn expression constructors;
- expression identity / `valkey`: a candidate identifier for an expression incarnation, whose exact lifecycle remains to be confirmed.

Do not assume these identifiers are interchangeable.

## 3. Process-expression syntax

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

## 4. Session-type syntax and polarity

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

## 5. Typing interface

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

## 6. Execution and communication

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

## 7. Representation and serialization caveats

The adapter in `proc/termexp/adapter/tc.go` translates between AST, message, and stored representations. In the inspected version, `MsgFromExpSpec` has no `Link` branch; `MsgToExpSpec` has a `Call` branch, but reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. The executor has no `Call` or `Link` branch. The `call` scenario in `test/e2e/pool_test.go` constructs a caller and a call expression, but the top-level `TestPool` does not run it (the subtest is commented out); the scenario also leaves its result assertion as a TODO and creates the callee declaration without defining a callee body. It therefore does not establish a successful call transition, even if run separately. These observations describe the current implementation and evidence limits; they do not establish that `Call` is independently implementable or that the missing branches are defects, because call semantics may depend on the unresolved `Spawn`/pool model. The adapter also contains these apparent asymmetries:

- `MsgToExpSpec` reconstructs `CallSpec` without `CommChnlPH` and `ContExp`, although those fields exist in the AST constructor. In the current AST, `LabSpec` also has a `ContExp` field; the message conversion reconstructs `LabSpec` without it.
- In case-expression conversions, label data appears to be read from a fixed `Lab` field rather than the current branch entry. This occurs in the message-to-AST conversion and in the stored-data-to-AST conversions for both specs and records.
- The send record conversion stores both continuation-channel and value-channel identifiers in one direction, but appears to restore only one in the reverse direction.
- The receive record conversion appears not to preserve `ContChnlID` symmetrically.
- Some receive conversions appear to write the communication-channel placeholder into the field that the reverse conversion reads as the newly bound channel. Specifically, `dataFromExpSpec` assigns `RecvSpecDS.Y` from `CommChnlPH`, although `dataToExpSpec` reads `Y` into `NewChnlPH`.

These are source-level discrepancies to validate with focused tests and call-path analysis. Their observable runtime impact is not established by this document.

## 8. Operational semantics: conservative scope

A formal reduction relation should distinguish at least:

- an expression that is ready to execute;
- an expression suspended while waiting for a peer;
- a communication whose peer has arrived;
- the resulting channel/linear-context update;
- continuation scheduling and persistence.

The current evidence supports treating execution as a stateful transition over an execution snapshot plus communication/exchange state. It does **not** yet justify importing a generic session-calculus semantics verbatim, nor asserting that each AST constructor has a complete reduction rule.

The first fully formalized rules should be limited to constructors whose typing and execution branches have both been checked end-to-end. Rules for calls and resource-management constructs should remain explicitly unspecified until their intended and implemented contracts are reconciled. `Spawn` is deferred to the pool-level analysis. `Link` should be investigated alongside recursive process definitions/calls, not conflated with `Fwd`.

## 9. Preliminary design direction: named-process calls

`Link` and `Call` both refer to named-process behavior, but they are not interchangeable syntax: `CallSpec` has a `ContExp` field, while `LinkSpec` has no continuation expression. This difference must be preserved in the language model unless a formal rule establishes an equivalent continuation mechanism for `Link`. Recursion may still be a property of the dependency graph among process definitions rather than a separate recursive-only construct; that question is distinct from the `Link`/`Call` continuation distinction.

This choice avoids making call behavior depend on whether the source expression happens to occur inside a definition. Context may still constrain whether a call is well-typed or executable, but the construct should not acquire unrelated meanings merely from its syntactic location unless the language rationale requires that distinction.

The supplied publication gives a useful reference model for named-process calls: a call `a ← p b` reduces `proc(a ← p b)` to `proc(P[a/x, b/y])` when the process definition `x ← p y = P` is in the definition environment. In this notation, `p` names the process definition; `a`, `b`, `x`, and `y` are channel names/placeholders in the call and definition. These letters should keep the roles assigned by the publication and must not be repurposed as identifiers for OrgLang process incarnations. The rule substitutes the actual channel names for the definition's placeholders and replaces the call term with the instantiated body in the publication's abstract configuration. This rule does not explicitly describe what happens to the calling process: it says nothing here about whether that process continues, stops, or is represented separately. It should therefore be used only as a comparison point for channel-name substitution, not as evidence for OrgLang's control-flow semantics. In OrgLang, invocation creates a new process incarnation connected to the invoking process through channels, and the `Call` specification includes a `ContExp` for the caller's continuation.

OrgLang's intended call semantics should not be collapsed into the publication's single-process replacement rule: invocation creates a new process incarnation connected to the invoking process through channels, and the invoking process continues through `ContExp`. This continuation is part of the intended language-level behavior; how snapshots, runtime components, channels, and pool state realize the transition remains an implementation question. Pool-level `Spawn` stays a distinct operation.

Pool-level `Spawn` has a concrete, separate role in the current implementation: its specification carries a process-declaration reference and optional references to existing process incarnations (`ProcCompRefs`). The pool adapter converts those references at the API boundary. This supports keeping pool-level instantiation/injection distinct from process-level named invocation. It does not by itself establish that `Call` and `Spawn` have identical lifecycle semantics.

The author has clarified the intended mapping for `LinkSpec`: `X` corresponds to the declaration's `LiabVar` (the new process's provider endpoint), and `Ys[i]` corresponds positionally to `AssetVars[i]` (the new process's client endpoints). The invoking process supplies the actual channels by naming its own channel placeholders; those actual channels are then passed, connected, or injected into the new incarnation according to the declaration's provider/client roles. Thus the mapping is positional, and `Ys` preserves the order of `AssetVars`.

There is also an important representation distinction: `symbol.ADT` represents a channel-placeholder name, while `identity.ADT` represents a channel identifier. Since `LinkSpec.X` and `LinkSpec.Ys` are currently typed as `identity.ADT`, this may be an implementation mismatch with the intended semantics. It is not yet proven to be a defect: we must check whether placeholder resolution is meant to happen before constructing `LinkSpec` or whether these fields should instead retain placeholder symbols. The supplied publication's call syntax `a ← p b₁ … bₙ` is a comparison point, not independent evidence for OrgLang's exact representation.

### Evidence note: pool spawning versus process-level invocation

The inspected pool expression API has a `Spawn` form whose implementation-level specification carries a process declaration reference (`ProcTermRef`) and optional references to process incarnations (`ProcCompRefs`). The `test/e2e/pool_test.go` scenarios use pool-level `Spawn` to instantiate a declared process and, in some cases, supply existing process incarnations as dependencies. This is evidence for a distinct pool-level instantiation operation in the current implementation, not yet a normative language rule.

By contrast, the process-level `Call` scenario uses a process name, a binding placeholder, channel placeholders, and a continuation. However, that scenario is not invoked by `TestPool`, its expected-result assertion is a TODO, and it creates the callee declaration without creating a corresponding process definition. It cannot establish the semantics of a complete call. The process definition API's inspected `Create` and `Retrieve` methods are stubs, which further limits conclusions from this path.

The intended direction is that process-level invocation creates a new incarnation connected to the invoking process through channels. For `Call`, the new incarnation begins executing independently and the invoking process may continue via `ContExp`. `Link` has no `ContExp`, so its control-flow rule must differ or obtain continuation behavior through some other explicit mechanism; the absence of this field alone does not establish that the invoking process terminates. Current pool API fields are clues about implementation boundaries, not a basis for deciding that question.

### Preliminary operational rules for `Call` and `Link`

These rules state the intended language-level distinction. They are not claims about the completeness of the current Go implementation.

#### `Call`

A call creates a fresh process incarnation and starts its body independently. The invoking process continues through `ContExp`.

**Preconditions**

- The named process definition is available.
- A fresh process-incarnation identifier can be chosen.
- The call's actual channel arguments can be matched to the declaration's formal channel parameters, preserving provider/client roles and the declaration's parameter order.

**Transition**

1. Instantiate the callee body by substituting the actual channels for the corresponding formal channel placeholders.
2. Add a fresh process incarnation running that instantiated body.
3. Continue the invoking process with `ContExp`.

The exact field-by-field mapping from `CallSpec` to declaration parameters is not confirmed. An illustrative `call` scenario in `test/e2e/pool_test.go` suggests the following interpretation: `BindChnlPH` names a channel through which the caller's continuation communicates with the callee's provider endpoint, while `ValChnlPHs` supplies existing channels for the callee's `AssetVars`, in declaration order. In that scenario, the caller's `ContExp` waits on `BindChnlPH`, and the supplied channel argument comes from the caller's `AssetVars`. However, this example cannot confirm the mapping: its result assertion is a TODO, the callee declaration is created without a corresponding process body, and the inspected `DefSpec` persistence methods are stubs. The adapter also maps the external `BindChnlPH` to internal `NewChnlPH` and does not preserve `ContExp` in the constructed `CallSpec`, so the current API conversion cannot be treated as a faithful semantic definition. Treat the proposed mapping as a hypothesis only. The inspected rationale repository contains no independent language-level rule that settles the question. The intended semantic point remains that the callee's execution and the caller's continuation both remain active after the call transition.

#### `Link`

`Link` creates a fresh incarnation but transfers control to it without an ordinary caller continuation.

**Preconditions**

- The named process definition is available, and a fresh process incarnation can be created.
- Resolve `X` and `Ys` in the invoking process's placeholder environment. `X` supplies the existing provider channel for the new process's `LiabVar`; `Ys[i]` supplies the channel for `AssetVars[i]`, in declaration order.
- The new process's provider channel has exactly the same **current residual session type** as the invoking process's provider channel.

**Transition**

1. Instantiate and start a fresh incarnation of the named process with those channel parameters.
2. Transfer provider-side ownership of the existing channel named by `X` to the new incarnation. The channel itself and its unique client's connection to it remain unchanged.
3. Preserve linearity: each channel has exactly one provider and exactly one client.
4. Transfer control to the new incarnation; the invoking incarnation has no ordinary `ContExp` to run.

The client can continue the same protocol on the same channel because the new incarnation takes over providing it with the same residual session type. This rule does not specify when the old incarnation's remaining state is reclaimed, or define failure and scheduling behavior.

#### Summary

- **Call:** create and run a new incarnation; the caller continues with `ContExp`.
- **Link:** create and run a new incarnation; transfer the existing provider channel and control to it; no ordinary caller continuation.
- **Fwd:** remains a distinct forwarding operation. The analogy `Link ≈ Call + Fwd` is explanatory only and is not asserted as an equivalence.

### Publication rules for forwarding

The author supplied these forwarding rules from the session-types publication:

```text
proc(d⁺ m ← c⁺ m) → !⁺mmsg(d⁺m, c⁺m)   id: forward+
proc(d⁻ m ← c⁻ m) → !⁻msrv(d⁻m, c⁻m)   id: forward−
```

In OrgLang, the publication's `msg` and `srv` actions map to `pub` and `sub`, respectively. This gives a concrete cross-language correspondence for interpreting the forwarding rules: the positive rule's message action corresponds to `pub`, and the negative rule's service action corresponds to `sub`.

Keep the publication's rules as source evidence rather than silently treating them as OrgLang rules. The exact meanings of the polarity markers and indexed symbols should be read from the surrounding publication definitions before deriving a stronger claim about endpoint replacement or channel rewiring.

For OrgLang `Link`, this suggests that its channel-proxying effect may be understood through the forwarding behavior represented by `pub`/`sub`, while `Link` additionally creates a new process incarnation and transfers control. These rules alone do not prove that OrgLang `Link` is formally equivalent to `Call` followed by `Fwd`, or that `Fwd` itself mutates channel identity; that equivalence requires the surrounding semantics and linearity invariants.

### Comparison with OrgLang `pub`/`sub` and `Fwd`

In the inspected `orglang/go-engine` source, the process communication-turn representation aligns with the author's mapping: `PubRec` stores a `ValExp` (the publication/message action), while `SubRec` stores a `ContExp` (the subscription/service continuation). The process executor's `FwdSpec` branch reads the forwarding endpoint's current session-type polarity and examines the next communication turn on that channel.

The inspected implementation behaves schematically as follows:

- With positive polarity, a waiting `SubRec` is redirected to the forwarding expression's communication channel; a pending `PubRec` is redirected to its continuation channel; if no turn exists, the forwarder records a `PubRec` carrying a `FwdRec`.
- With negative polarity, the redirection targets are reversed for the existing `SubRec`/`PubRec` cases; if no turn exists, the forwarder records a `SubRec` carrying a `FwdRec`.
- The branches update linear-variable bindings and schedule the affected peer's continuation where applicable. Some channel-side fields remain marked `TODO` in the implementation, so these observations are not a complete correctness proof.

This supports interpreting `Fwd` as a polarity-sensitive operation that connects the pending publication/subscription protocol action across two endpoints, rather than as a generic global replacement of channel identifiers. It is a useful implementation comparison for `Link`'s provider-channel handoff, but does not yet establish that the whole `Link` transition can be implemented by simply composing the existing `Call` and `Fwd` branches. In particular, `Link` must create the new incarnation, transfer control, preserve the one-provider/one-client invariant, and ensure compatibility with the client's current residual session type.

### Trace of channel placeholders versus channel identifiers

The inspected process AST and execution snapshot expose a concrete distinction:

- Ordinary expression specifications such as `CallSpec` use `symbol.ADT` for fields such as `NewChnlPH` and `ValChnlPHs`. These are placeholder names, and the execution snapshot's `LinearVars` is keyed by `symbol.ADT`; for example, the `Send` executor looks up `execSnap.LinearVars[termExp.ValChnlPH]` to resolve a placeholder to its current linear-channel record, which contains a channel identifier.
- Stored/runtime records use `identity.ADT` for resolved channel IDs in fields such as `SendRec.ValChnlID` and `ContChnlID`. The adapter explicitly converts between placeholder symbols and stored channel identities in the relevant paths.
- `LinkSpec.X` and `LinkSpec.Ys`, however, are currently typed as `identity.ADT`/`[]identity.ADT`, while the author's intended meaning is that the invoking process names the placeholders from which the actual channels are obtained. `LinkSpec.Via()` also returns an empty symbol, and the inspected expression adapter has no `Link` conversion branch; the process executor has no `Link` branch either.

This is a concrete representation mismatch **if** `LinkSpec.X` and `Ys` are supposed to carry caller-side placeholder names at the AST/expression-spec stage. A possible alternative is that the design intends these fields to carry already-resolved channel IDs and resolve them through another mapping, but no such path has been established in the inspected code. The evidence therefore supports flagging the current type choice as a likely implementation inconsistency with the stated intent, not yet declaring the correct fix. A focused follow-up should decide whether the AST fields should be `symbol.ADT`/`[]symbol.ADT`, then trace serialization and resolution before changing `go-engine` (which is out of scope for this rationale-only work).
The author has clarified the exact typing condition for `Link`: the new process's provider channel, declared in `Dec`, must have exactly the same session type as the invoking process's provider channel at the moment `Link` is invoked. This is equality of the current residual session type, not merely compatibility of the initial declared types. If the old provider channel has residual type S at the transition point, the new provider channel must also have type S, allowing the existing client to continue the same protocol without changing its expected session type.

### Preliminary operational rule for `Link`

This is the intended abstract language-level rule. It describes process/channel behavior, not the Go representation or a required implementation strategy.

**Preconditions**

- The named process definition is available, and a fresh process incarnation can be created.
- Resolve `X` and `Ys` in the invoking process's placeholder environment. `X` supplies the actual channel for the new process's `LiabVar`; `Ys[i]` supplies the actual channel for `AssetVars[i]`, in declaration order.
- The new process's provider channel has exactly the same **current residual session type** as the invoking process's provider channel.

**Transition**

- Create and start a fresh incarnation of the named process, instantiating its channel parameters from those actual channels.
- Transfer the existing provider channel named by `X` into the new incarnation as its `LiabVar`; the channel and its existing client connection remain unchanged. No client reconnection is required.
- Preserve linearity: each channel has exactly one provider and exactly one client.
- Transfer control to the new incarnation. There is no ordinary continuation of the invoking incarnation; `Link` has no `ContExp`.

**Result and limits**

The existing client can continue the same protocol on the same channel because the new incarnation takes over providing that channel, with the same residual session type. This rule does not specify when the old incarnation's stored state is reclaimed, nor does it define failure or scheduling behavior. The analogy `Link ≈ Call + Fwd` is explanatory only; the rule does not require that decomposition.

## 10. Open questions for the next verification pass

1. What is the precise relationship among `TermQN`, `ProcQN`, `ProcTermQN`, declaration references, and expression identity?
2. (Resolved for `Link`.) `Ys[i]` corresponds to `AssetVars[i]` in declaration order.
3. What is the intended semantic relationship between named-process invocation, process creation (`Spawn`), and the pool model, and which parts belong to each layer?
4. (Partly resolved.) The intended `Link` transition is stated in the rule above. Remaining open: lifecycle of the old incarnation's state, and any failure/scheduling guarantees beyond the abstract transition.
5. Where should name resolution, recursion checks, and type checks be enforced? The language-level meaning of `LinkSpec.X` and `Ys` is settled: they name placeholders in the invoking process; the Go field-type discrepancy is an implementation issue.
6. (Resolved at the language-design level.) OrgLang `Call` starts a new incarnation while the caller continues through `ContExp`. Still open: confirm the field-by-field mapping of `BindChnlPH` and `ValChnlPHs` to the callee's declaration parameters; the current test only suggests a mapping and does not assert the result.
7. Are type-level `Link`, `Up`, and `Down` resolved before the currently observed type-checking cases?
8. What are the contracts of `Acqure`, `Accept`, `Detach`, and `Release`?
9. What are the full invariants for `ChnlBS`, provider/client orientation, and linear-context updates?
10. Are the conversion asymmetries listed above reachable in the actual execution path, and which tests can establish their impact?
11. What exact transition semantics do subscription/publication and exchange-turn records implement?
12. Must all branches of a `Case` preserve equivalent linear contexts, and where is that enforced?

## 11. Non-goals

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation and rationale.



## Author clarification: invocation creates a new process incarnation

The language author has confirmed the following intended call semantics:

- Invoking a named process creates a **new process incarnation** connected to the invoking process through channels. Invocation is not merely textual substitution/unfolding inside the existing incarnation.
- The new incarnation begins executing independently of the invoking process.
- The invoking process may continue along `ContExp`.
- The call's channel arguments connect the new incarnation to the invoking process according to the call/declaration contract. The positional mapping is established: `X` corresponds to `LiabVar`, and `Ys[i]` corresponds to `AssetVars[i]`.

This settles the intended control-flow direction and positional channel mapping at a conceptual level. It does not specify scheduling guarantees, failure behavior, or lifecycle details.

Keep the following boundaries explicit:
- **Established design direction:** `Call` creates a new incarnation; it begins executing independently; the invoking process may continue via `ContExp`; channels connect the two. `Link` differs from `Call` in that its AST has no `ContExp`.
- **Established at the abstract level:** `Link` transfers control to a new incarnation and does not schedule an ordinary continuation for the invoking process.
- **Still open:** remaining typing premises beyond provider session-type equality, scheduling and persistence details, and failure/lifecycle rules.
- **Separate operation:** pool-level `Spawn` remains distinct from process-level named invocation.
- **Implementation evidence only:** existing Go structures and pool APIs may inform implementation choices but do not determine the intended semantics by themselves.


## 12. A simple shared model for process transitions

We can describe `Call` and `Link` without introducing a large formal configuration. For now, use three basic ideas:

- **Process incarnation:** one running instance of a process.
- **Channel:** a connection with exactly one provider and exactly one client.
- **Placeholder environment:** the mapping from channel-placeholder names used in a process expression to the actual channels they refer to.

A placeholder is a name used by the expression; the channel is the connection that name resolves to. For `Link`, resolve `X` and each entry in `Ys` in the invoking process's environment before starting the target process.

### `Call`

1. Find the named process definition.
2. Create a fresh process incarnation and supply its channels according to the call/declaration contract.
3. Start the new incarnation.
4. Let the invoking process continue with `ContExp`.

The exact field-by-field mapping from `CallSpec` to declaration parameters remains unspecified.

### `Link`

1. Find the named process definition.
2. Resolve `X` and `Ys` in the invoking process's placeholder environment. `X` supplies the target process's provider channel; `Ys[i]` supplies its client channels in declaration order.
3. Require the target provider channel to have the same **current residual session type** as the existing channel named by `X`.
4. Start a fresh incarnation and transfer provider-side ownership of that existing channel to it. The channel and its client connection do not change.
5. Transfer control to the new incarnation; there is no ordinary caller continuation.

Throughout the transition, each channel still has exactly one provider and one client. The lifecycle of the old incarnation's remaining state is not specified here.

### Why these constructs differ

- **Call** starts a new incarnation and the caller continues.
- **Link** starts a new incarnation, transfers provider ownership of an existing channel, and transfers control.
- **Fwd** remains a separate forwarding operation. The analogy `Link ≈ Call + Fwd` is only an intuition, not a proven equivalence.

This is the current level of detail needed to state the intended behavior. We can add formal notation later, only where it makes a rule clearer.
