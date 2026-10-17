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

This is a description of the process/session-type layer. Pool and transaction semantics are out of scope.

The terms **confirmed**, **tentative**, and **open** are used as follows:

- **Confirmed**: directly supported by the currently inspected implementation or its comments.
- **Tentative**: a plausible interpretation, but the complete call path or invariant has not yet been verified.
- **Open**: the implementation inspected so far does not establish the contract.

## 2. Process declarations and definitions

A process declaration is represented by `DecSpec` with fields:

- `TermQN`: the declaration's qualified name;
- `LiabVar`: the endpoint on which the process acts as provider;
- `AssetVars`: endpoints on which it acts as client.

These provider/client descriptions come from comments in `proc/termdec/core/core.go`. Whether and where the order of `AssetVars` is semantically significant still requires verification.

A process definition is represented by `DefSpec{ProcQN, ProcES}`; `DefRec` contains a `Ref`. The inspected `Create`/ `Retrieve` implementation in `proc/termdef/core/core.go` appears to be a stub, so this representation alone does not establish the persistence contract.

Keep these names distinct until their relationships are demonstrated by code. In particular, `LinkSpec.X` and `LinkSpec.Ys` are `identity.ADT` values, not channel placeholders (`symbol.ADT`), so they should not be documented as channel arguments without further evidence:

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
| `LinkSpec` | `ProcTermQN`, `X`, `Ys` (`identity.ADT`) | Existing name for a construct under investigation. The current design direction is one named-process call construct for both recursive and non-recursive calls; whether `LinkSpec` should be renamed or unified with `CallSpec` remains open |
| `FwdSpec` | `CommChnlPH`, `ContChnlPH` | Forward between endpoints |
| `CallSpec` | `CommChnlPH`, `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, `ContExp` | Candidate representation of a named-process call; exact contract and relationship to `LinkSpec` remain open pending the process/pool model |
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

The inspected `takeWith` contains execution branches for `Close`, `Wait`, `Send`, `Recv`, `Lab`, `Case`, and `Fwd`. The current `LabSpec` AST includes `ContExp`, but its message adapter does not preserve that field; whether a label-selection continuation is semantically required remains open. It does not contain branches for `Call`, `Spawn`, `Link`, `Acqure`, `Accept`, `Detach`, or `Release`; those constructors have no execution branch in this dispatcher in the inspected version. This is a statement about the inspected implementation, not by itself a conclusion that the language design is defective. `Spawn` and the call mechanism are interdependent because both may rely on the unresolved model of process creation and pools. Consequently, no complete operational rule for `Call` or `Spawn` is specified here. The current design direction is a single named-process call construct for recursive and non-recursive calls; recursion would arise from cyclic dependencies among process definitions rather than requiring a separate recursive-call construct. This is provisional and does not settle how process creation works. Channel forwarding (`Fwd`) remains a distinct operation.

Communication is not necessarily completed in one pass. For example, when the counterpart of a `Close`/`Wait` or a send/receive interaction is not yet available, the execution path can register a subscription and return without completing that interaction. When the peer is found, the implementation updates exchange state, allocates channel identifiers, updates linear-variable records, and may schedule the continuation.

This is an implementation-level description. The exact transition relation, message ownership, and invariants for subscriptions, publications, and exchange turns still need to be formalized from all producer/consumer call paths.

## 7. Representation and serialization caveats

The adapter in `proc/termexp/adapter/tc.go` translates between AST, message, and stored representations. In the inspected version, `MsgFromExpSpec` has no `Link` branch; `MsgToExpSpec` has a `Call` branch, but reconstructs `CallSpec` without `CommChnlPH` and `ContExp`. The executor has no `Call` or `Link` branch, and an end-to-end test in `test/e2e/pool_test.go` does not establish a successful call transition. These observations describe the current implementation and evidence limits; they do not establish that `Call` is independently implementable or that the missing branches are defects, because call semantics may depend on the unresolved `Spawn`/pool model. The adapter also contains these apparent asymmetries:

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

The current design direction is to use one language construct for invoking a named process, whether the invocation participates in recursion or not. Recursion would be a property of the dependency graph among process definitions (for example, a cycle in the references), rather than a separate call syntax solely for recursive cases. This is a design hypothesis, not a finalized grammar or operational semantics.

This choice avoids making call behavior depend on whether the source expression happens to occur inside a definition. Context may still constrain whether a call is well-typed or executable, but the construct should not acquire unrelated meanings merely from its syntactic location unless the language rationale requires that distinction.

The distinction between invoking a named process and creating a new process must remain explicit. `Spawn`, `Call`, and pool behavior appear related, but their precise relationship is unresolved. The operational contract for calls should therefore not be fixed independently of the process-lifecycle/pool model.

The meanings of `LinkSpec.X` and `LinkSpec.Ys` are also open. Their intended meanings must be established from language semantics, not inferred from the Go implementation types (`identity.ADT` versus `symbol.ADT`). In particular, this draft does not assume that they are channel arguments.

## 10. Open questions for the next verification pass

1. What is the precise relationship among `TermQN`, `ProcQN`, `ProcTermQN`, declaration references, and expression identity?
2. Is the order of `AssetVars` significant for positional channel matching?
3. What is the intended semantic relationship between named-process invocation, process creation (`Spawn`), and the pool model, and which parts belong to each layer?
4. Should `Link` and `Call` be one language construct? The current design direction favors one named-process call for both recursive and non-recursive cases, with recursion arising from cyclic dependencies between process definitions; the final syntax and runtime contract remain open.
5. What do identity-valued `X`/`Ys` refer to in the intended language semantics, independent of their implementation types, and where should name resolution, recursion checks, and type checks be enforced?
6. Are type-level `Link`, `Up`, and `Down` resolved before the currently observed type-checking cases?
7. What are the contracts of `Acqure`, `Accept`, `Detach`, and `Release`?
8. What are the full invariants for `ChnlBS`, provider/client orientation, and linear-context updates?
9. Are the conversion asymmetries listed above reachable in the actual execution path, and which tests can establish their impact?
10. What exact transition semantics do subscription/publication and exchange-turn records implement?
11. Must all branches of a `Case` preserve equivalent linear contexts, and where is that enforced?

## 11. Non-goals

This draft does not define pool or transaction semantics, resource-allocation policy, fairness, deadlock freedom, or a complete metatheory (such as preservation/progress). Those require a separate pass over the pool/transaction implementation and rationale.

