# Spawn: semantic design notes

> **Status: preliminary design draft.** This document records decisions made during design discussion and separates them from hypotheses and unresolved questions. It does not specify pool or transaction semantics.

## Scope and method

The goal is to define the semantic role of `spawn` at the boundary between process semantics and the future pool/transaction model. Process and session-type behavior is treated as existing context; pool and transactional types will be designed separately. The design should avoid silently importing implementation behavior into language semantics.

Primary context:
- [Processes and session types](https://github.com/orglang/rationale/blob/main/about-processes-and-session-types/README.md), especially Section 7 (intended semantics of `Call` and `Link`) and Section 8 (the publication's distinct cut/spawn rule).
- [go-workspace issue #85](https://github.com/orglang/go-workspace/issues/85), including its discussion of the semantic model and the unresolved role of `Spawn`.
- [Grilling design-interview method](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md): resolve the current decision frontier in rounds, record recommendations, and defer dependent questions.

## Decision register

### D1 — Scope of this design

**Status: agreed.**

Define `spawn` as a boundary between the process model and the future pool model. Specify the minimum contract required at that boundary, while leaving the semantics of pools and transactions themselves for separate work.

Consequences:
- Process-level concepts such as process definitions, incarnations, channel environments, and session protocols may be used as established context.
- Pool selection, transactional agreement, resource reservation, fairness, and other pool-level policies must not be invented here.
- Where `spawn` depends on a future pool contract, record the dependency explicitly.

### D2 — Is `spawn` a source-language construct?

**Status: agreed direction; exact semantic surface remains open.**

For this design, treat `spawn` as an engine-level operation, not as a presumed standalone user-written language construct. The existence of an AST constructor named `SpawnSpec` does not establish that users directly write a `spawn` operation.

The semantic design may describe the abstract engine operation and its contract without deciding yet which source-language construct, if any, invokes it.

### D3 — Meaning of `call`

**Status: interpretation grounded in the existing rationale; confirm edge cases during the next round.**

Section 7 of *Processes and session types* describes `Call` as named-process invocation: resolve the named process, explicitly map its declared channel parameters to existing channels, start a fresh process incarnation with its own execution state and channel environment, inject a distinct provider channel for communication with the caller, and allow the caller's continuation to proceed after the incarnation starts. Explicitly mapped channels are transferred to the new incarnation; distinct formal parameters must map to distinct channels under linearity.

On this basis, `call` is not being treated as a request to reuse an arbitrary already-running incarnation. The fresh-incarnation behavior is the current intended contract in the rationale, although its authoritative language source and implementation remain unverified there.

This distinction must be preserved: `Call` has process-invocation semantics, while this design investigates the separate engine-level `spawn` operation and its relationship to the pool boundary. Do not assume that `Call` is implemented using `Spawn`, or that their semantic contracts are identical.

## Current semantic questions

The following questions are intentionally unresolved until the relevant decisions are discussed:

1. What entity does the engine-level `spawn` operation accept: a named process definition, a process body, an allocation request, or another abstract value?
2. What observable result does `spawn` produce, if any: a fresh channel, a process-incarnation reference, a success/failure outcome, or only a state transition?
3. Which preconditions belong to process semantics, and which are delegated to the future pool/transaction contract?
4. What happens when spawning cannot be serviced: waiting, a semantic failure, or another explicitly defined outcome?
5. How are `Call`, process-expression `Link`, and engine-level `Spawn` related, without assuming one is implemented through another?
6. How does the publication's cut rule (fresh channel allocation, spawned process, and continuation) inform OrgLang's intended semantics without being treated as proof that OrgLang has an equivalent source-level construct?

These are design questions, not claims about current runtime behavior. Implementation observations should be recorded separately from language-level rules.

## Next round

Resolve the semantic identity and input/output contract of engine-level `spawn` before deciding its failure and scheduling behavior. The next round should ask only questions whose prerequisites are settled by D1–D3.
