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

## Working interpretation

**Preliminary hypothesis.** `Call` and `Spawn` may belong to different semantic layers:

- `Call` is the language-level process-invocation operation with an intended contract about named-process resolution, channel mapping, a fresh incarnation, and caller continuation.
- `Spawn` may be an engine-level mechanism that participates in realizing a request to create an incarnation, potentially at the process–pool boundary.
- The relationship between these layers is not established. In particular, it is not yet known whether `Spawn` is the internal fulfillment step for `Call`, a lower-level API used by more than one construct, or an independent operation with a distinct contract.

This hypothesis avoids inventing a second language-level “request” while also avoiding the unsupported claim that `Call` and `Spawn` are identical or that one is implemented through the other.

## Design constraints established so far

The following constraints define the scope of the investigation:

1. Define only the minimum contract at the process–pool boundary; defer pool and transaction semantics to separate work.
2. Treat `spawn` as an engine-level operation for now. Do not infer source-language syntax from an AST type name.
3. Use the existing rationale's intended `Call` contract as the current semantic baseline, while retaining its evidence and implementation caveats.
4. Keep process-level semantics, engine operations, pool API behavior, and prototype reductions distinct unless evidence establishes a mapping.
5. Record uncertainty rather than silently resolving it from implementation details or from the publication's different calculus.

## Open research agenda

The next investigation should compare the relevant definitions and call paths across sources, then resolve the following dependencies in order:

1. **Semantic identity:** what does each occurrence of `Spawn` denote in the AST, pool API, and prototype? Are these separate operations or representations of one contract?
2. **Relation to `Call`:** does the language-level `Call` contract delegate to an engine-level `Spawn`, or is their relationship merely conceptual? What evidence would establish that mapping?
3. **Input and output:** what does the engine-level operation receive, and what observable result does it produce? Candidate results such as a fresh channel, an incarnation reference, or a state transition must remain hypotheses until supported.
4. **Boundary preconditions:** which conditions are guaranteed by process semantics, and which belong to the future pool contract?
5. **Unavailability and failure:** what does the process-level contract require when an incarnation cannot be created? Waiting, failure, and other outcomes remain open; no pool policy is assumed here.
6. **Channel allocation:** which source, if any, requires a fresh channel to be created as part of spawning? Do not generalize the publication's cut rule without evidence.
7. **Lifecycle and observability:** when is creation considered complete, what can the caller observe, and what happens to the continuation? These details must be derived from the relevant OrgLang contract rather than assumed from the publication.

These are research questions rather than an interview checklist. Conclusions should be recorded alongside their source and evidential status, and only promoted to semantic rules when the evidence supports them.
