# Spawn at the process–pool boundary

> **Status: preliminary research draft.** This document investigates the intended semantics of `spawn` in OrgLang. It separates source evidence, working hypotheses, and unresolved design questions. It is not a normative specification and does not define pool or transaction semantics.

## Purpose and scope

The investigation focuses on the semantic boundary between process invocation and the future pool model. It aims to identify the minimum contract that process semantics requires from the pool-facing mechanism, without pre-empting the design of pools, transactions, resource allocation, or scheduling.

The term `spawn` is treated as an engine-level operation for purposes of this investigation, not as proof that OrgLang has a standalone source-language construct named `spawn`. The existence of an AST constructor named `SpawnSpec` is evidence of a representation in the implementation, not by itself evidence of user-facing syntax or complete runtime semantics.

## Sources and evidential method

Primary sources:

- [Processes and session types](https://github.com/orglang/rationale/blob/main/about-processes-and-session-types/README.md), particularly Section 7 on the intended semantics of `Call` and `Link`, and Section 8 on the publication's cut/spawn rule.
- [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including comments discussing the semantic model and the unresolved status of `Spawn`.
- [Grilling method](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md), used as a method for systematically identifying uncertainty and dependencies. Its interview format is not the format of this research document.

Claims below are distinguished as **Observed** (directly present in a source), **Inferred** (a working interpretation of evidence), or **Open** (the sources do not settle the matter). Publication rules are evidence for what the publication specifies, but are not automatically OrgLang rules. Implementation names and structures likewise do not establish language semantics on their own.

## Evidence from the existing rationale

### The intended contract of `Call`

**Observed — rationale, Section 7.** `Call` is described as invocation of a named process. The intended contract resolves the named process, maps its declared channel parameters to existing channels, starts a fresh process incarnation with separate execution state and a channel environment, injects a distinct provider channel for communication with the caller, and allows the caller's continuation to proceed once the incarnation has started. Explicitly mapped channels are transferred to the new incarnation; distinct formal parameters must map to distinct channels under linearity.

The same section says that the contract's authoritative language source and implementation mapping remain unverified. It also explicitly avoids assuming that `Call` is implemented using `Spawn`.

**Implication.** The term “request to start a process” should not be introduced as a second abstract operation without evidence. At the language level, `Call` already expresses process invocation and its intended outcome includes a fresh incarnation. It is therefore plausible that a call is the language-level request whose fulfillment requires a lower-level process-creation mechanism. That is a useful hypothesis, not yet an established equivalence between `Call` and `Spawn`.

### The publication's cut/spawn rule

**Observed — rationale, Section 8.** The publication's rule `x ← P ; Q` allocates a fresh channel, starts a process running `P` with that channel substituted for `x`, and continues the original process as `Q` with the same channel substituted. This is a particular rule combining channel allocation, process creation, and continuation.

**Limitation.** This rule does not establish that OrgLang's `SpawnSpec` has the same semantics, that `Spawn` is a source-language construct, or that process-pool behavior is part of the publication's rule. Those correspondences require separate evidence.

### Distinct implementation representations

The existing rationale distinguishes a process-expression `SpawnSpec`, a pool API `SpawnSpec2`, and a separate prototype reduction associated with `proto/rast2`. These representations must not be treated as interchangeable merely because they share the name “spawn.” The current executor's lack of a `Spawn` branch is implementation evidence, not a complete definition of intended language semantics.

## Evidence from issue discussion and implementation

### Issue #85 discussion

**Observed — issue comments, provisional rather than normative.** The comments transferred from #84 make the intended separation more specific:

- `Call` inside a process is described as the trigger for requesting particular work, identified by `qn`; it is explicitly distinguished from a separate `spawn` message.
- The engine-level act of creating a process incarnation is described as an internal operation that services `Call`.
- An inter-pool agreement may make service possible under specified conditions, but the agreement itself does not create the process.
- The details of resource provisioning and reservation, the point at which the incarnation is created, and behavior when service is unavailable remain unresolved.
- The comments also preserve an unresolved alternative: if no existing agreement enables service, the caller may wait for an agreement to change, or a transaction may be initiated to change it. Neither behavior is selected as final semantics.

Sources: [issue comment on the relationship between `Call` and spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290893), [comment on transactional types and process spawning](https://github.com/orglang/go-workspace/issues/85#issuecomment-6230290639), and [end-to-end scenario for servicing `Call`](https://github.com/orglang/go-workspace/issues/85#issuecomment-6232198226).

This discussion is the strongest current evidence for the intended conceptual relationship: `Call` is the process-level request/trigger, while creation of the incarnation is an internal engine operation. Since the comments explicitly label this material as working hypotheses rather than a specification, the relationship should be recorded as **provisional**, not treated as settled.

### Implementation representations

**Observed — process-expression AST.** In [`proc/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/proc/termexp/core/core.go), `CallSpec` contains `CommChnlPH`, `NewChnlPH`, `ProcTermQN`, `ValChnlPHs`, and `ContExp`. The same file's `SpawnSpec` contains `CommChnlPH`, `ProcTermQN`, `NewChnlPHs`, and `ContExp`. These shapes overlap, but differ in their channel fields and do not by themselves define the semantic relation between the operations.

**Observed — pool API representation.** In [`pool/termexp/core/core.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/core/core.go), `SpawnSpec2` instead contains a reference to a process term (`ProcTermRef`) and references to process incarnations (`ProcCompRefs`). In [`pool/termexp/adapter/tc.go`](https://github.com/orglang/go-engine/blob/main/pool/termexp/adapter/tc.go), this pool-level representation is adapted to the SDK's `Spawn` operation. This is evidence of a pool API operation that names a process definition and existing process incarnations; it is not evidence that it has the same transition rule as process-expression `SpawnSpec`.

**Observed — incomplete execution path.** The process executor in [`proc/compexec/core/core.go`](https://github.com/orglang/go-engine/blob/main/proc/compexec/core/core.go) retains a commented-out legacy `SpawnSpecOld` branch. The inspected source does not establish a complete active execution semantics for process-expression `SpawnSpec`. The existence of an SDK adapter for pool-level `SpawnSpec2` must not be mistaken for a complete implementation of the language-level process operation.

**Consequence.** There are at least two distinguishable representations called `Spawn`: a process-expression AST node and a pool API operation. The current evidence does not justify collapsing them into one operation, nor does it show that either is the internal operation servicing `Call`.

## Working interpretation

**Current working hypothesis, supported by issue discussion but not yet normative.** `Call` is the process-level trigger/request for a named process. The engine coordinates servicing that call; when the required conditions are met, an internal creation operation starts a fresh incarnation and binds the relevant channels. The pool layer and its agreements may constrain whether and how the call can be serviced, but an agreement is not itself a process creation event.

The word `spawn` is ambiguous across the inspected materials. It may refer to a process-expression AST construct, a pool API operation, or an abstract internal creation step. The evidence does not yet establish that these are the same semantic operation. In particular:

- Do not model a separate `spawn` message as the caller's request; the issue discussion explicitly distinguishes this from `Call`.
- Do not state that `Call` is implemented through the AST-level `SpawnSpec` or pool-level `SpawnSpec2`; no such implementation mapping has been established.
- Do not infer that pool agreement itself creates an incarnation.
- Do not choose between waiting for a changed agreement and initiating a transaction to obtain one; both are still discussed as alternatives.
- Do not specify resource reservation order or the precise moment of creation before the pool/transaction model is designed.

This interpretation narrows the investigation: the immediate task is to determine whether OrgLang needs a semantically distinct `Spawn` at all, and if so, what role the existing AST and pool API representations play. That can be resolved only by reconciling the intended process semantics with the distinct implementation abstractions and the future pool contract.

## Design constraints established so far

The following constraints define the scope of the investigation:

1. Define only the minimum contract at the process–pool boundary; defer pool and transaction semantics to separate work.
2. Treat `spawn` as an engine-level operation for now. Do not infer source-language syntax from an AST type name.
3. Use the existing rationale's intended `Call` contract as the current semantic baseline, while retaining its evidence and implementation caveats. Current issue discussion provisionally treats `Call` as the process-level trigger and incarnation creation as an internal engine operation.
4. Keep process-level semantics, engine operations, pool API behavior, and prototype reductions distinct unless evidence establishes a mapping.
5. Record uncertainty rather than silently resolving it from implementation details or from the publication's different calculus.

## Open research agenda

The next investigation should compare the relevant definitions and call paths across sources, then resolve the following dependencies in order:

1. **Semantic identity:** what does each occurrence of `Spawn` denote in the process AST, pool API, and prototype? Are these separate operations or representations of one contract?
2. **Relation to `Call`:** issue discussion provisionally describes `Call` as the trigger and creation as an internal engine operation. Is there a distinct semantic operation corresponding to any current `Spawn` representation, or is `Spawn` merely an implementation/API label? What evidence would establish the mapping?
3. **Input and output:** what does the engine-level operation receive, and what observable result does it produce? Candidate results such as a fresh channel, an incarnation reference, or a state transition must remain hypotheses until supported.
4. **Boundary preconditions:** which conditions are guaranteed by process semantics, and which belong to the future pool contract?
5. **Unavailability and failure:** what does the process-level contract require when an incarnation cannot be created? Waiting, failure, and other outcomes remain open; no pool policy is assumed here.
6. **Channel allocation:** which source, if any, requires a fresh channel to be created as part of spawning? Do not generalize the publication's cut rule without evidence.
7. **Lifecycle and observability:** when is creation considered complete, what can the caller observe, and what happens to the continuation? These details must be derived from the relevant OrgLang contract rather than assumed from the publication.

These are research questions rather than an interview checklist. Conclusions should be recorded alongside their source and evidential status, and only promoted to semantic rules when the evidence supports them.
